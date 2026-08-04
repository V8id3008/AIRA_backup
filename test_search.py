from search.web_search import search_web

results = search_web("latest AI news")

print(f"Found {len(results)} results")

for result in results:
    print("\n----------------")
    print(result.get("title"))
    print(result.get("href"))