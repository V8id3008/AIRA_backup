from search.web_search import search_web

def gather_research(query):

    results = search_web(query)

    context = ""

    for r in results:

        title = r.get("title", "")
        body = r.get("body", "")
        url = r.get("href", "")

        context += f"""
Title: {title}

Summary:
{body}

Source:
{url}

-----------------------
"""

    return context