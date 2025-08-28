import requests
import json

class SearchAgent:
    """
    A class that handles queries using SerpAPI for search
    and Groq API for summarization/processing.
    """

    def __init__(self, serp_api_key: str, groq_api_key: str):
        self.SERP_API_KEY = serp_api_key
        self.GROQ_API_KEY = groq_api_key

    # ---------------------------
    # SerpAPI search
    # ---------------------------
    def search_serp(self, query: str):
        url = "https://serpapi.com/search.json"
        params = {"q": query, "api_key": self.SERP_API_KEY}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    # ---------------------------
    # Groq API processing
    # ---------------------------
    def process_groq(self, text: str):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "compound-beta-mini",
            "messages": [
                {"role": "system", "content": "You are an AI assistant that summarizes search results."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            # Groq returns text in choices[0].message.content
            return data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            return {"error": str(e)}

    # ---------------------------
    # Main query method
    # ---------------------------
    def query(self, user_query: str):
        # 1️⃣ Search SerpAPI
        serp_results = self.search_serp(user_query)
        if "error" in serp_results:
            return f"SerpAPI error: {serp_results['error']}"

        # 2️⃣ Extract top snippets
        snippets = []
        for item in serp_results.get("organic_results", []):
            if "snippet" in item:
                snippets.append(item["snippet"])
        if not snippets:
            return "No search results found."

        combined_text = "\n".join(snippets[:5])  # Top 5 snippets

        # 3️⃣ Send to Groq
        groq_response = self.process_groq(combined_text)

        # 4️⃣ Fallback: if Groq fails, return SerpAPI snippets
        if isinstance(groq_response, dict) and "error" in groq_response:
            return f"Groq API error: {groq_response['error']}\n\nSerpAPI results:\n{combined_text}"

        return groq_response

# ---------------------------
