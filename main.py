from Database.setup_data import setup_database
from Search.semantic_search import semantic_search

#setting up the database
setup_database()

print("\nSemantic Search Ready. Type your query below (or type 'exit' to quit):")
while True:
    query = input("\nQuery: ").strip()
    if query.lower() == "exit":
        break

    result = semantic_search(query, top_k=3)

    for r in result["matches"]:
        print(f"\n{r['title']} (Score: {r['score']:.4f})")
        print(f"Source: {r['source']}")
        print(f"{r['text'][:300]}...\n")
