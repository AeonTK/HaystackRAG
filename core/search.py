import os
from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument

from components.websearch.customsearchapi import CustomSearchApiWebSearch

load_dotenv()

SEARCH_PARAMS = {
    "key": os.environ.get("GOOGLE_API_KEY"),
    "cx": os.environ.get("SEARCH_ENGINE_ID"),
    "num": 3,
    "q": None,
    "lr": "lang_en",
    "gl": "us",
    "dateRestrict": "y[1]",
}


def generate_search_pipeline():
    """Adds components to the given pipeline and connects them (i.e creates a search pipeline).
    The pipeline searching the web using Google's Custom Search API.
    The search pipeline takes a query as input and returns a list of documents."""
    search_pipeline = Pipeline()
    web_search = CustomSearchApiWebSearch(search_params=SEARCH_PARAMS)
    link_content = LinkContentFetcher()
    html_converter = HTMLToDocument()
    
    search_pipeline.add_component("search", web_search)
    search_pipeline.add_component("fetcher", link_content)
    search_pipeline.add_component("converter", html_converter)

    search_pipeline.connect("search.links", "fetcher.urls")
    search_pipeline.connect("fetcher.streams", "converter.sources")
    
    return search_pipeline

