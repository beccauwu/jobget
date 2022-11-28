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

## Usage

Run the cli tool with `python jobget-cli.py <options>`



