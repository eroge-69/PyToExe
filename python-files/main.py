import wikipedia

wikipedia.set_lang("en")
query=input("اساءل")
results=wikipedia.search(query)
print("النتاءج")
page=wikipedia.page(results[0])
print(page .title)
print(page.summary)