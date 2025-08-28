from Groq_ai import SearchAgent
from local_memory import LocalMemory
from playwright.sync_api import sync_playwright
from Scrappingscripts.maps import MapsScraper
from Scrappingscripts.Wiki import WikipediaFetcher
from Scrappingscripts.googlesearchone import GoogleSearcher
# ------------------ Keys ------------------
SERP_KEY = "8594b0ba672133b4a15bdbb93d48f94a38c98ab4fbb00fc4884a957122c66233"
GROQ_KEY = "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"

# ------------------ Agents ------------------
groq_agent = SearchAgent(SERP_KEY, GROQ_KEY)
memory = LocalMemory()
google_searcher = GoogleSearcher("AIzaSyAXAb7aeVjs6Ix91bHvbzWSgtf_Pk1Nrag", "46d399959e73a40e8")

# ------------------ Abuse Generator Tool ------------------
# ------------------ Abuse Generator Tool ------------------
def abuse_generator_tool(user_message: str, tone: str = "medium") -> str:
    """
    Generates a dynamic abusive reply using Groq.
    """
    # Direct abusive corpus string (extend as needed)
    abusive_corpus = """
    bewakoof, chutiya, pagal, nalayak, baklol, harami, gadha, haramzada, khota,
    kamina, murkh, chichora, faltu, bawli, loda, gandu, chutmar, madarchod, 
    harami kutta, saale, bhosdike, etc...
    """

    # Build prompt for Groq
    prompt = f"""
You are a chatbot. The user said: "{user_message}"
Use the following abusive corpus to generate a reply in the same offensive tone.
Tone level: {tone}
Corpus: {abusive_corpus}

Reply naturally in Hinglish/Hindi in 1-3 sentences.
Do NOT exceed 150 words.
"""

    # Directly create a new Groq client call instead of using groq_agent
    from groq import Groq
    groq_client = Groq(api_key="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")  # Use same key as groq_agent
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a sassy, offensive assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()




def google_search_tool(query: str, max_results: int = 5) -> str:
    """
    Performs Google Custom Search and returns a concise text summary (titles + snippets)
    limited to 800 characters for LLM consumption.
    """
    output = google_searcher.search(query, max_results=max_results)
    results = output.get("results", [])

    combined_text = ""
    for item in results:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        combined_text += f"{title}: {snippet} "

        # Stop early if approaching 800 chars
        if len(combined_text) >= 800:
            break

    # Hard truncate if slightly exceeded
    if len(combined_text) > 800:
        combined_text = combined_text[:800] + "..."

    return combined_text.strip()


# ------------------ Memory Tool ------------------
def memory_tool(action, key=None, value=None, platform=None, user_id=None, password=None):
    if action == "store_fact" and key and value:
        return memory.store_fact(key, value)
    elif action == "get_fact" and key:
        return memory.get_fact(key)
    elif action == "delete_fact" and key:
        return memory.delete_fact(key)
    elif action == "store_credential" and platform and user_id and password:
        return memory.store_credential(platform, user_id, password)
    elif action == "get_credential" and platform:
        return memory.get_credential(platform)
    elif action == "delete_credential" and platform:
        return memory.delete_credential(platform)
    elif action == "list_all":
        return memory.list_memory()
    else:
        return "Invalid action or missing parameters"
def scrape_address_tool(address: str) -> dict:
    """Tool function for TOOLS to scrape Google Maps info for an address."""
    with sync_playwright() as p:
        scraper = MapsScraper(p, headless=True)
        result = scraper.scrape_address(address)
        scraper.close()
    return result
# Initialize the Wikipedia fetcher once
wiki_fetcher = WikipediaFetcher()

def get_wiki_text(query: str) -> str:
    """
    Wrapper function for chatbot to get Wikipedia content.
    """
    try:
        text = wiki_fetcher.get_content(query)
        return text
    except Exception as e:
        print(f"⚠️ Wikipedia fetch error: {e}")
        return ""
# ------------------ Search Tool ------------------
def search_query(query: str) -> str:
    """
    Wrapper function for the search agent to be used in TOOLS.
    """
    return groq_agent.query(query)

# ------------------ TOOLS Dictionary ------------------
TOOLS = {
    # "search": {
    #     "description": "Searches the web and summarizes results using SerpAPI + Groq",
    #     "params": {"query": "string"},
    #     "func": search_query
    # },
    "google_search": {
        "description": "Searches the web and summarizes results using Google API and returns combined snippets or results",
        "params": {
            "query": "Search query string",
            "max_results": "Maximum number of results (default 5)"
        },
        "func": google_search_tool  # This calls your GoogleSearcher wrapper
    },
    "memory_tool": {
        "description": (
            "Stores, retrieves, deletes, or lists user facts and platform credentials. "
            "Actions: store_fact, get_fact, delete_fact, store_credential, "
            "get_credential, delete_credential, list_all."
        ),
        "params": {
            "action": "Specify what to do: store_fact, get_fact, delete_fact, "
                      "store_credential, get_credential, delete_credential, list_all",
            "key": "Fact name (for fact actions)",
            "value": "Fact value (for store_fact)",
            "platform": "Platform name (for credentials actions)",
            "user_id": "User ID (for store_credential)",
            "password": "Password (for store_credential)"
        },
        "func": memory_tool
    },
    "maps_scraper": {
        "description": "Scrapes Google Maps for a given address, returning name, website, phone, and working hours",
        "params": {"address": "string"},
        "func": scrape_address_tool
    },
    "wikipedia": {
        "description": "Fetches Wikipedia content for a given query and returns plain text",
        "params": {"query": "string"},
        "func": get_wiki_text
    },
"abuse_generator": {
    "description": (
        "Generates a dynamic abusive reply in Hinglish/Hindi using a local corpus and Groq. "
        "Use this tool ONLY if the user input contains offensive, abusive, or rude language. "
        "Tone can be low, medium, or high depending on severity."
    ),
    "params": {
        "user_message": "The offensive message from the user",
        "tone": "Tone of abuse: low, medium, high (default: medium)"
    },
    "func": abuse_generator_tool
}
}

