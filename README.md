# ballharbor
A natural language search engine for NBA highlights using the NBA Stats API, `spacy`, and a bit of fuzzy searching. 

## Demo

INSERT VIDEO HERE

## Installation

1. Clone the repository
2. Install the required packages (nba_api is dependent on an old numpy so we run the command with the `--no-deps` flag)
```bash
pip install -r requirements.txt --no-deps
```
3. Either try out the notebook or run it as an API
```bash
uvicorn api:app --reload
```

## About the Project

Currently, the NBA does not allow for their API to be used for any commercial purposes, so this project is not able to be ran in a production environment. However, I built out a simple frontend for demonstration purposes. The shown demo is a NextJS frontend that just queries this API.

## How it Works

The search engine is comprised of two parts, the `EntityExtractor` and `SearchEngine`. The `EntityExtractor` is dedicated to spellcheck, entity recognition, and entity linking. The goal is for the entity extractor to feed our search engine with easily parameterized queries. The `SearchEngine` takes those parameters and then queries the `nba_api` library to find and filter the specified clips.


