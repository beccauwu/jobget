import asyncio
import httpx
import requests
import json
import math
from ..schemas.schemas import *
from typing import Union, Literal, Dict, List, Any, ClassVar
from pydantic import parse_obj_as


class NoResponseFound(Exception):
    """Response was not found
    """
    pass


class NoParameterFound(Exception):
    """No parameter was found
    """
    pass


class NoArgsGiven(Exception):
    """No argument was given
    """
    pass


class InsufficientArgs(Exception):
    pass


class JobGetClient():
    """Handles requests.s to jobs API and dealing with them.

        ...

        Attributes
        ----------
        url : `str`
            url for API endpoint
        response : `Response`
            the most recent parsed response from API
        params : `SearchParams`
            parameters to include in an API call
        args : `ClientArgs`
            arguments for different client functionality
        history : `ClientHistory`
            keeps a list of previous values
        save : `bool `
            boolean indicating whether to save to history by default
        status : `int`
            the current status of the client

        Methods
        ----------
        get : `() => None`
            execute query based on current attributes
        set_params : `(params: SearchParams) => None`
            set search parameters
        set_args : `(args: ClientArgs) => None`
            set client arguments
        detect_languages `() => None`
            detect languages defined in `arglang` from response 
        save_response `(path: str) => None`
            save response to file
        
        Notes
        ----------
        Please don't set attributes directly, use set functions - the functions save history which setting attributes doesn't, and does additional formatting/validation

    """
    def __init__(
            self, *,
            save_by_default: bool = True,
            url: str = 'https://jobsearch.api.jobtechdev.se/search'
            ) -> None:

        """Inits Client with default save behaviour and API endpoint

        Parameters
        ----------
        save_by_default : `bool`
            sets the client save attribute, defaults to True
        url : `str`
            sets the API endpoint
        """
        self.url = url
        self.response: Union[QueryResponse, None] = None
        self.params: Union[SearchParams, None] = None
        self.args: Union[Args, None] = None
        self.history: Union[ClientHistory, None] = None
        self.save: bool = save_by_default
        self.status: ClientStatus = ClientStatus(code=0)
        self.errors: List[Exception] = []
        self.session = requests.Session()
        self.result: Union[List[Ad], None] = None
    async def exec(self) -> None:
        """Execute the query based on the current attributes .
        """
        self.status.code = 1
        if not self.params:
            self.status.code = 3
            self.errors.append(NoParameterFound("No parameters found"))
        headers = {'accept': 'application/json'}
        self.params.offset = 0
        def __no_limit(q: SearchParams) -> Dict[str,Any]:
            q.limit = 0
            return q.dict(exclude_none=True)
        
        async with httpx.AsyncClient(headers=headers) as client:
            res_total = await client.get(self.url, params=__no_limit(self.params))
            res_total.raise_for_status()
            total = QueryResponse(**res_total.json()).total.value
            expecting = math.ceil(total / 100)
            self.status = ClientStatus(code=1, expecting=expecting, received=0)
            tasks: List = []
            self.params.limit = 100
            for i in range(expecting):
                self.params.offset = i*100
                tasks.append(client.get(self.url,params=self.params.dict(exclude_none=True)))
            res = await asyncio.gather(*tasks, return_exceptions=True)
            json_res = []
            for r in res:
                if isinstance(r, Exception):
                    self.errors.append(r)
                    self.status.errors += 1 if self.status.errors else 1
                else:
                    json_res.append(r.json())
                self.status.received += 1 if self.status.received else 1
            hits = []
            for r in json_res:
                hits.extend(r['hits'])
            resp = {**json_res[0], 'hits': hits}
            self.response = QueryResponse(**resp)
        self.status.code = 0
        

    def set_params(
            self,
            params: Dict[str,Union[str, List[str], bool, int]],
            save: bool = True
            ) -> None:

        """Set search params .

        Parameters
        ----------
        params : `Dict[str,Union[str, List[str], bool, int]]`
            parameters to set
        save : `bool`
            whether to save to history, overrides default save behaviour
        """
        try:
            new_params = parse_obj_as(SearchParams, params)
            if self.__save(save, self.params):
                if not self.history:
                    self.history = ClientHistory(
                        params=self.params,
                    )
                self.history.params.append(self.params)
            self.params = new_params
        except Exception as e:
            self.errors.append(e)

    def set_args(
            self,
            args: Dict[str, Union[str, List[str], bool]],
            save: bool = True
            ) -> None:
        """Set the arguments to the client .

        Parameters
        ----------
        args : `Dict[str, Union[str, List[str], bool]]`
            arguments to set
        save : `bool`
            whether to save to history, overrides default save behaviour
        """
        try:
            new_args = parse_obj_as(Args, args)
            if self.__save(save, self.args):
                if not self.history:
                    self.history = ClientHistory(
                        args=[self.args],
                    )
                self.history.args.append(self.args)
            self.args = new_args
        except Exception as e:
            self.errors.append(e)
    def __save(self, save: bool, param: Any = None) -> bool:
        return param is not None and ((self.save and save) or save)
    def detect_languages(self) -> None:
        """Detect languages based on the search query .

        Raises
        ----------
        NoArgsGiven
            if no arguments are given
        InsufficientArgs
            if no languages are given in arguments
        NoResponseFound
            if no response is found in client
        """
        if not self.args:
            raise NoArgsGiven("No args given")
        if not self.args.lang:
            raise InsufficientArgs("No languages defined")
        if not self.response:
            raise NoResponseFound("No response found")
        from langdetect import detect
        for ad in self.response.hits:
            ad.language = detect(" ".join(ad.description.text.split()[:10]))
    
    def filter_emails(self) -> None:
        """Filter out adas withou emails .

        Raises
        ----------
        NoResponseFound
            if no response is found in client
        """
        self.status.code = 1
        if not self.response:
            self.status.code = 3
            raise NoResponseFound("No response found")
        self.result = [(ad for ad in self.response.hits
                           if ad.application_details.email
                           or ad.employer.email)]
        self.status.code = 2
    
    def clear_errors(self):
        self.status.code = 0
        self.errors = []

    def save_response(self, path: str) -> None:
        """Save the response to a JSON file .

        Parameters
        ----------
        path : `str`
            path to save the file to
        
        Raises
        ----------
        NoResponseFound
            if no response is found in client
        """
        if not self.response:
            raise NoResponseFound("No response found")
        with open(path, "w") as f:
            json.dump(self.response.dict(), f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import doctest
    doctest.testmod(extraglobs={"client": JobGetClient()})