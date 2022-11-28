import getopt
import json
import math
import sys
import asyncio
from datetime import datetime
from io import open
from typing import Dict, List, Callable, Tuple, Union, Any

from langdetect import detect
from tqdm import tqdm

from schemas import schemas
from src.util import print_all_opts
from src.client import JobGetClient


def get_languages(
    q: List[schemas.Ad],
    langs: List[str]) -> List[schemas.Ad]:
    """Gets the probable language of the ad and filters for the specified languages

    Args:
        q (List[schemas.Ad]): _description_
        langs (List[str]): _description_

    Returns:
        List[schemas.Ad]: _description_
    """
    res = []
    totals: Dict[str, int] = {}
    pbar= tqdm(total=len(q), desc=f"Detecting languages")
    for i in range(len(q)):
        pbar.set_description(f"Detecting languages ({i+1}/{len(q)})")
        o= q[i]
        first_ten_words = ' '.join(o.description.text.split()[:10])
        lang = str(detect(first_ten_words))
        if lang in langs:
            res.append(o)
            totals[lang] = totals.get(lang, 0) + 1
        o.language = lang
        res.append(o)
        pbar.update(1)
    pbar.close()
    print(f"Found {len(res)} ads with language in {langs}")
    print(f"Totals: {totals}")
    return res

def get_emails(q: List[schemas.Ad]) -> List[schemas.Ad]:
    """Filters for ads with emails

    Args:
        q (List[schemas.Ad]): List of ads

    Returns:
        List[schemas.Ad]: Filtered List of ads
    """
    res = []
    pbar= tqdm(total=len(q), desc=f"Filtering for ads with email")
    for i in range(len(q)):
        pbar.set_description(f"Filtering for ads with email ({i+1}/{len(q)})")
        o= q[i]
        if not o.application_details.email and not o.employer.email:
            pbar.update(1)
            continue
        res.append(o)
        pbar.update(1)
    pbar.close()
    print(f"Found {len(res)} ads with email")
    return res

def write_json(res:List[schemas.Ad], filename:str):
    """Writes List of ads to json file

    Args:
        res (List[schemas.Ad]): Ads to write
        filename (str): Filename to write to (without .json), writes to results/res_{filename}.json
    """
    print(f"Writing {len(res)} ads to file...")
    res_json = [ad.dict() for ad in res]
    with open(f"results/res_{filename}.json", "w+", encoding="utf-8") as results_file:
        json.dump(res_json, results_file, indent=4, ensure_ascii=False)

async def expected_total(client:JobGetClient, query:str, remote:bool) -> int:
    """Sends empty query to get expected total

    Args:
        query (str): Query to search for
        remote (bool): Remote or not

    Returns:
        int: Number of results
    """
    params = {"q": query, "limit": 0}
    if remote:
        params['remote'] = True
    client.set_params(params)
    await client.exec()
    while True:
        if client.response:
            return client.response.total.value

async def get_query(client: JobGetClient) -> Tuple[List[schemas.Ad], Union[Exception, None]]:
    """Gets query 100 ads at a time (due to limit)

    Args:
        params (schemas.QueryParams): Params for query

    Returns:
        List[schemas.Ad]: Returned queries parsed to pydantic models
    """
    await client.exec()
    while True:
        if client.status.code == 1:
            continue
        if client.status.code == 2:
            return client.response.hits, None
        if client.status.code == 3:
            return client.response.hits, client.errors[0]

def parse_ads(ads: List[dict]) -> List[schemas.Ad]:
    """Parses ads to pydantic models

    Args:
        ads (List[dict]): unparsed ads

    Returns:
        List[Ad]: parsed ads
    """
    from pydantic.error_wrappers import ValidationError
    pbar = tqdm(total=len(ads), desc="Parsing ads")
    parsed_ads = []
    for i in range(len(ads)):
        pbar.set_description(f"Parsing ads ({i+1}/{len(ads)})")
        try:
            parsed_ads.append(schemas.Ad(**ads[i]))
        except ValidationError:
            print(f"{[i]}: {ads[i]['driving_license']}")
        pbar.update(1)
    pbar.close()
    return parsed_ads

def build_html(ads: List[schemas.Ad]) -> str:
    """Builds html to display results
    
    Args:
        ads (List[schemas.Ad]): List of ads
    """
    html = ""
    for ad in ads:
        html += f"""<p>{ad.headline}</p>
        <h2>{ad.employer.name}</h2>
        <p>{ad.description.text}</p>
        <p>{ad.application_details.url}</p>
        <p>{ad.language}</p>
        <hr>
        """
    return html

def send_emails(ads: List[schemas.Ad]):
    """Automatically sends emails to employers
    Attaches cv and cover letter in language of the ad

    Args:
        ads (List[schemas.Ad]): Ads to send emails to
    """
    import json
    import mimetypes
    import os
    import re
    import smtplib
    import sys
    from email import encoders
    from email.headerregistry import Address
    from email.message import EmailMessage
    from email.mime.application import MIMEApplication
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import make_msgid

    def send_email(params: schemas.EmailParams):
        msg = MIMEMultipart()
        msg['Subject'] = params.subject
        msg['From'] = ''
        msg['To'] = params.recipient
        msg.attach(MIMEText(body, 'html'))
        a = params.attachments
        with open(a.CV, 'r+b') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(a.CV))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(a.CV)
            msg.attach(part)
        with open(a.CoverLetter, 'r+b') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(a.CoverLetter))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(a.CoverLetter)
            msg.attach(part)
        # s = smtplib.SMTP('localhost')
        # s.send_message(msg)
        # s.quit()
        #append email to file
        with open('results/emails.txt', 'a') as f:
            f.write(f"{datetime.utcnow()} - {params.recipient}{os.linesep}")
            f.write(msg.as_string())
            f.write(f"{os.linesep}{os.linesep}")
    for ad in ads:
        email = ad.application_details.email if (
            ad.application_details) else (
                ad.employer.email) if ad.employer else None
        if not email:
            continue
        subject = f"Jobb: {ad.headline}"
        lang = ad.language
        cv = f"att/CV_{lang}.pdf"
        if not os.path.isfile(cv):
            print(f"Missing CV for {lang}")
            print("using english CV instead")
            cv = "att/CV_en.pdf"
        cover_letter = f"att/CoverLetter_{lang}.pdf"
        if not os.path.isfile(cover_letter):
            print(f"Missing cover letter for {lang}")
            print("using english cover letter instead")
            cover_letter = "att/CoverLetter_en.pdf"
        body = f"""
        <h1>{ad.headline}</h1>
        <p>{ad.description.text if ad.description else None}</p>
        <p><a href="{ad.webpage_url}">{ad.webpage_url}</a></p>
        """
        attachments = schemas.EmailAttachments(CV=cv, CoverLetter=cover_letter)
        params = schemas.EmailParams(recipient=email, subject=subject, body=body, attachments=attachments)
        send_email(params)
    
def filter_by_keywords(
    ads: List[schemas.Ad],
    keywords: List[str]
    ) -> List[schemas.Ad]:
    """Filter query based on keywords

    Args:
        ads (List[schemas.Ad]): List of ads
        keywords (List[str]): List of keywords

    Returns:
        List[schemas.Ad]: filtered List of ads
    """
    print("Filtering ads...")
    filtered_ads = []
    for ad in ads:
        if any((keyword in ad.description.text) or (
                keyword in ad.headline) for keyword in keywords):
            filtered_ads.append(ad)
    print(f"Found {len(filtered_ads)} ads")
    return filtered_ads
def parse_args() -> Dict[str, Any]:
    """Parse command line arguments

    Returns:
        schemas.Args: parsed arguments
    """
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hq:l:f:ersw",
            ["help", "query=", "lang=","filter=","email", "remote", "send", "write"])
    except getopt.GetoptError as err:
        print(err)
        print_all_opts()
        sys.exit(2)
    parsed = {}
    for o, a in opts:
        if o in ("-h", "--help"):
            print_all_opts()
            sys.exit(1)
        elif o in ("-q", "--query"):
            parsed['query'] = a
        elif o in ("-l", "--lang"):
            if ',' in a:
                parsed['lang'] = a.split(',')
            else:
                parsed['lang'] = [a]
        elif o in ("-e", "--email"):
            parsed['email'] = True
        elif o in ("-r", "--remote"):
            parsed['remote'] = True
        elif o in ("-s", "--send"):
            parsed['send'] = True
        elif o in ("-f", "--filter"):
            if ',' in a:
                parsed['filter'] = a.split(',')
            else:
                parsed['filter'] = [a]
        elif o in ("-w", "--write"):
            parsed['write'] = True
        else:
            assert False, "unhandled option"
    return parsed

async def main():
    client = JobGetClient()
    args = parse_args()
    client.set_args(args)
    query = args.get('query')
    lang = args.get('lang')
    email = args.get('email')
    remote = args.get('remote')
    send = args.get('send')
    write = args.get('write')
    if not query:
        raise ValueError("Query is required")
    await expected_total(client, query, remote)
    #params=args minus send, write
    response, err = await get_query(client)
    if err is not None:
        print(str(err))
    if lang:
        if write:
            await client.detect_languages(lang)
            write_json(client.response.hits, "languages")
        else:
            await client.detect_languages(response, lang)
    if email:
        await client.filter_emails()
        if write:
            if client.status.code == 2:
                write_json(client.result, "emails")
            elif client.result:
                write_json(client.result, "emails")
                err = client.errors[0]
                if err:
                    print(f"Error: {err}")
                print(f"Status: {client.status.dict()}")
        else:
            if client.result:
                response = client.result
            else:
                print(f"Status: {client.status.dict()}")
    if send:
        send_emails(response)
    write_json(response, f"{query}_final")
    print("Done!")

if __name__ == '__main__':
    asyncio.run(main())