# google_search.py
import requests
import os
from dotenv import load_dotenv

class GoogleSearcher:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, safe: str = "off", max_results: int = 10, snippet_limit: int = 800):
        """
        Returns:
            {
                "results": list of dicts (title, link, snippet),
                "combined_snippets": single string of all snippets (truncated to snippet_limit)
            }
        """
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": max_results,
            "safe": safe
        }
        response = requests.get(self.base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        results = []
        snippets = []
        for item in data.get("items", []):
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })
            if snippet:
                snippets.append(snippet)

        combined_snippets = " ".join(snippets)[:snippet_limit]
        return {"results": results, "combined_snippets": combined_snippets}


# Example usage
if __name__ == "__main__":
    load_dotenv()  # Load from .env

    API_KEY = os.getenv("GOOGLE_API_KEY")
    CSE_ID = os.getenv("GOOGLE_CSE_ID")

    searcher = GoogleSearcher(API_KEY, CSE_ID)
    query = "Amitabh Bachchan"
    output = searcher.search(query)

    print("Combined Snippets:\n", output["combined_snippets"])
    print("\nIndividual Results:")
    for idx, r in enumerate(output["results"], 1):
        print(f"{idx}. {r['title']}\n{r['link']}\n{r['snippet']}\n")
