from elasticsearch import Elasticsearch
import json

ES_HOST = 'http://localhost:9200'
ES_INDEX = 'f1'

es = Elasticsearch(hosts=ES_HOST)


def print_results(title: str, response: dict):
    """Helper to print query results in a readable format."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    hits = response.get("hits", {}).get("hits", [])
    aggs = response.get("aggregations", {})

    if hits:
        for hit in hits:
            print(json.dumps(hit["_source"], indent=2, default=str))
    if aggs:
        print(json.dumps(aggs, indent=2, default=str))


# 1. FULL-TEXT SEARCH
# Demonstrates: text field search with relevance scoring
# Use case: Search races by name - "monaco" finds "Monaco Grand Prix"
def search_race_by_name(name: str):
    response = es.search(index=ES_INDEX, body={
        "query": {
            "match": {
                "race_name": name
            },
        },
        "collapse": {
            "field": "race_id"
        },
        "_source": ["race_name", "season", "circuit_country"],
        "size": 5
    })
    print_results(f"Full-Text-Search: races matching '{name}'", response)


# 2. FUZZY SEARCH
# Demonstrates: tolerance for typos - "Hamilten" still finds "Hamilton"
# Use case: Search bar where users may mistype driver names
def search_driver_fuzzy(surname: str):
    response = es.search(index=ES_INDEX, body={
        "query": {
            "fuzzy": {
                "driver_surname": {
                    "value": surname,
                    "fuzziness": "AUTO"  # AUTO: allows 1-2 character edits
                }
            },
        },
        "_source": ["driver_forename", "driver_surname", "driver_nationality"],
        "size": 1
    })
    print_results(f"Fuzzy-Search: drivers matching '{surname}'", response)


if __name__ == "__main__":
    search_race_by_name("monaco")  # 1. Full-text-search
    search_driver_fuzzy("hamilten")  # 2. Fuzzy search (typo)
