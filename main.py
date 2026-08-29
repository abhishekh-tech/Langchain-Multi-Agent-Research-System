from src.tools.tools import web_search,scrape_url

# output = web_search("Latest news on AI research")
# print(output)

r = web_search.invoke("What is the latest news on nepal-tibet flood? ")
print(r)