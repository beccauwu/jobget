<p align="center">
    <img src="assets/banner.png" height="200"/>
</p>

# About

Python script for searching jobs in Sweden using the [JobTech](https://jobsearch.api.jobtechdev.se/) API

Still very much in progress, will be updating regularly.

# Functionality

## Currently working:

- Search for jobs with given query
- Filter ads for languages (technically every language supported but results are mostly Swedish/English) - language is added to `ad.language`
- Filter for ads that have an email address in them
- Query only jobs that are probably open for remote work
- write json results to file (can choose to keep different files for all the different filter stages or filter results to one file)

## Untested:

- Filter for keywords in ad description text

## Planned:

- Send emails with CV & Cover letter to emails in applications with SMTPlib
- Save search queries to file so you can choose from history
- Choose filenames
- Make some sort of a reader to parse json

# Structure

## Pydantic

I'm working on creating pydantic models for everything to keep things typesafe

## Other

The code is messy atm but i'll work on tidying it up.
I've made a client class in ./client which I'm working on, it's untested.
The working functionality is all from jobget-cli.py which is the original app

# Usage

## Requirements

For now you do need python installed to use the client

## Procedure

Steps 3&4 are optional but highly recommended to not clutter your OS python installation

1. Clone this repo

   * `git clone https://github.com/beccauwu/jobget.git`
2. cd into the dir

   * `cd jobget`
3. Run the automated setup script 

    * `source ./setup`
        This will:
        1. Create a virtual environment
        2. Activate the virtual environment
        3. Upgrade pip
        4. Install dependencies
4. Run the script

   * `python jobget-cli.py <options>`

```
usage: jobget-cli.py [options]
    options:

    ---short-------long--------------description----
    -h         | --help            | print this help
    -q <query> | --query=<query>   | search for <query> (required)
    -l <lang>  | --lang=<lang>     | search for <lang>  (sv, en)
    -f <csv>   | --filter=<csv>    | filter results by <csv>
    -e         | --email           | search for ads with email
    -r         | --remote          | search for remote jobs
    -s         | --send            | send applications to ads with email
    -w         | --write           | write results from different stages to separate files
```

### Usage in your own code

To use the client in your app,
