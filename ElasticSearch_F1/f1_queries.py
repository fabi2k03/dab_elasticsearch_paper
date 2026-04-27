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


# 3. FILTER QUERY
# Demonstrates: exact filtering on keyword/numeric fields (no relevance scoring)
# Use case: Find all races in a specific country
def filter_races_by_country(country: str):
    response = es.search(index=ES_INDEX, body={
        "query": {
            "term": {
                "circuit_country": country
            }
        },
        "collapse": {
            "field": "circuit_name.keyword"
        },
        "sort": [
            {"season": {"order": "asc"}}
        ],
        "_source": ["race_name", "season", "circuit_location"],
        "size": 10
    })
    print_results(f"Filter: all races in '{country}'", response)


# 4. BOOL QUERY
# Demonstrates: combining multiple conditions (must, filter, should)
# Use case: "All races where Verstappen finished in the top 3 after 2016"
def bool_query_podium_finishes(surname: str, min_season: int, max_position: int):
    response = es.search(index=ES_INDEX, body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"driver_surname": surname}}  # full-text, affects score
                ],
                "filter": [
                    {"range": {"season": {"gte": min_season}}},  # numeric range filter
                    {"range": {"finish_position": {"lte": max_position}}}
                ]
            }
        },
        "_source": ["driver_forename", "driver_surname", "race_name", "season", "finish_position", "constructor_name"],
        "size": 10
    })
    print_results(f"Bool Query: {surname} podium finishes (pos <= {max_position}) from {min_season} onwards", response)


# 5. AGGREGATION Terms
# Demonstrates: grouping by a keyword field (like SQL GROUP BY)
# Use case: All-time wins leaderboard per driver
def agg_wins_per_driver(top_n: int = 10):
    response = es.search(index=ES_INDEX, body={
        "size": 0,
        "query": {
            "term": {"finish_position": 1}  # only count race wins
        },
        "aggs": {
            "wins_per_driver": {
                "terms": {
                    "field": "driver_surname.keyword",
                    "size": top_n,
                    "order": {"_count": "desc"}
                }
            }
        }
    })
    print_results(f"Aggregation: Top {top_n} drivers by race wins", response)

# 6. AGGREGATION Sum
# Demonstrates: numeric aggregation (sum) grouped by a keyword field
# Use case: Total championship points per constructor (all-time)
def agg_points_per_constructor(top_n: int = 10):
    response = es.search(index=ES_INDEX, body={
        "size": 0,
        "aggs": {
            "points_per_constructor": {
                "terms": {
                    "field": "constructor_name.keyword",
                    "size": top_n,
                    "order": {"total_points": "desc"}
                },
                "aggs": {
                    "total_points": {
                        "sum": {"field": "points"}   # sum up all points per constructor
                    }
                }
            }
        }
    })
    print_results(f"Aggregation: Top {top_n} constructors by total points", response)

# 7. AGGREGATION - Data Histogram
# Demonstrates: grouping by time intervals (per year)
# Use case: How many races were held each decade?
def agg_races_per_season():
    response = es.search(index=ES_INDEX, body={
        "size": 0,
        "aggs": {
            "unique_races_per_season": {
                "terms": {
                    "field": "season",
                    "size": 100,
                    "order": {"_key": "asc"}
                },
                "aggs": {
                    "race_count": {
                        "cardinality": {"field": "race_id"}   # count distinct races, not results
                    }
                }
            }
        }
    })
    print_results("Aggregation: Number of distinct races per season", response)

# 8. MULTI-MATCH SEARCH
# Demonstrates: searching across multiple fields at once
# Use case: General search box that searches both circuit name and country
def multi_match_search(query: str):
    response = es.search(index=ES_INDEX, body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["race_name", "circuit_name", "circuit_country"]
            }
        },
        "_source": ["race_name", "circuit_name", "circuit_country", "season"],
        "size": 5
    })
    print_results(f"Multi-Match Search: '{query}' across race, circuit and country fields", response)

if __name__ == "__main__":
    search_race_by_name("monaco")  # 1. Full-text-search
    search_driver_fuzzy("hamilten")  # 2. Fuzzy search (typo)
    filter_races_by_country("Italy")  # 3. Filter (exact)
    bool_query_podium_finishes("verstappen", 2016, 3)  # 4. Bool query
    agg_wins_per_driver(10)  # 5. Aggregation: wins
    agg_points_per_constructor(10)  # 6. Aggregation: points
    agg_races_per_season()  # 7. Aggregation: per season
    multi_match_search("British")  # 8. Multi-match
