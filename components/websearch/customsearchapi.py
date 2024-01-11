import os
import logging
from typing import Dict, List, Optional, Any
import requests
from haystack import Document, component, default_to_dict, ComponentError

logger = logging.getLogger(__name__)


API_BASE_URL = "https://www.googleapis.com/customsearch/v1"


class CustomSearchApiError(ComponentError):
    ...


@component
class CustomSearchApiWebSearch:
    """
    Search engine using Custom Search API. Given a query, it returns a list of URLs that are the most relevant.


    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        top_k: Optional[int] = 10,
        allowed_domains: Optional[List[str]] = None,
        search_params: Optional[Dict[str, Any]] = None,
    ):
        """
        :param api_key: API key for the SearchApi API.  It can be
        explicitly provided or automatically read from the
        environment variable GOOGLE_API_KEY (recommended).
        :param top_k: Number of documents to return.
        :param allowed_domains: List of domains to limit the search to.
        :param search_params: Additional parameters passed to the Custom Search API.
        For example, you can set 'num' to 100 to increase the number of search results.
        See the [SearchApi website](https://developers.google.com/custom-search/v1/overview) for more details.
        """
        if api_key is None:
            try:
                api_key = os.environ["GOOGLE_API_KEY"]
            except KeyError as e:
                raise ValueError(
                    "CustomSearchApiWebSearch expects an API key. "
                    "Set the GOOGLE_API_KEY environment variable (recommended) or pass it explicitly."
                ) from e
        self.api_key = api_key
        self.top_k = top_k
        self.allowed_domains = allowed_domains
        self.search_params = search_params or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this component to a dictionary.
        """
        return default_to_dict(
            self, top_k=self.top_k, allowed_domains=self.allowed_domains, search_params=self.search_params
        )

    @component.output_types(documents=List[Document], links=List[str])
    def run(self, query: str):
        """
        Search the Custom Search API for the given query and return the results as a list of Documents and a list of links.

        :param query: Query string.
        """
        
        self.search_params["q"] = query


        try:
            response = requests.get(url=API_BASE_URL, params = self.search_params)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
        except requests.Timeout:
            raise TimeoutError(f"Request to {self.__class__.__name__} timed out.")

        except requests.RequestException as e:
            raise CustomSearchApiError(f"An error occurred while querying {self.__class__.__name__}. Error: {e}") from e

        # Request succeeded
        json_result = response.json()

        # organic results are the main results from the search engine
        items = []
        if "items" in json_result:
            for result in json_result["items"]:
                items.append(
                    Document.from_dict({"title": result["title"], "content": result["snippet"], "link": result["link"]})
                )

        documents = items

        links = [result["link"] for result in json_result["items"]]

        logger.debug("Custom Search API returned %s documents for the query '%s'", len(documents), query)
        return {"documents": documents[: self.top_k], "links": links[: self.top_k]}
