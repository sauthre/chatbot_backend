# wiki.py
import requests

class WikipediaFetcher:
    """
    Fast Wikipedia fetcher. Returns plain text content for a query.
    Handles minor spelling issues using opensearch.
    Limits output to 500 characters.
    """

    def __init__(self, user_agent: str = "Mozilla/5.0"):
        self.headers = {"User-Agent": user_agent}

    def get_content(self, query: str) -> str:
        """
        Returns plain text content of the first matching Wikipedia page,
        limited to 500 characters. Returns empty string if no page found.
        """
        # Step 1: Find correct page title
        search_resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "opensearch",
                "search": query,
                "limit": 1,
                "namespace": 0,
                "format": "json"
            },
            headers=self.headers,
            timeout=5
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()
        if not search_data[1]:
            return ""  # no match

        page_title = search_data[1][0]

        # Step 2: Fetch plain text content
        parse_resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "explaintext": True,
                "titles": page_title,
                "format": "json"
            },
            headers=self.headers,
            timeout=5
        )
        parse_resp.raise_for_status()
        pages = parse_resp.json()["query"]["pages"]
        page = next(iter(pages.values()))
        content = page.get("extract", "")

        # Step 3: Limit to 500 characters
        return content[:500]
