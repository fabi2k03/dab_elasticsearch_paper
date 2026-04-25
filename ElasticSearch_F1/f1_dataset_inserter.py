from elasticsearch import Elasticsearch, helpers

ES_HOST = 'http://localhost:9200'
ES_INDEX = 'f1'
DATASET_PATH = "../f1_dataset"

"""
text ... for fields which should be searched inside. So texts like "Monaco Grand Prix" can be searched by using the keyword "monaco"
keyword ... for fields you want to filter or group by exactly (e.g. group by country)
text + keyword ... on some fields i want both functionality - to search them fuzzily and aggregate them by exact values
integer/float ... numeric fields, enables range queries and numeric aggregations
date ... used that elasticsearch understands chronological order and enables filter by time ranges
geo_point ... stores lat/lon coordinates - with this type visualizations in kinbana can be created
"""
MAPPING = {
    "mappings": {
        "properties": {
            # Race
            "race_id": {"type": "integer"},
            "race_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "season": {"type": "integer"},
            "round": {"type": "integer"},
            "race_date": {"type": "date", format: "yyyy-MM-dd"},

            #Sprints
            "race_id": {"type": "integer"},
            "driver_id": {"type": "integer"},
            "number": {"type": "integer"},
            "grid": {"type": "integer"},
            "position": {"type": "integer"},
            "points": {"type": "float"},
            "laps": {"type": "integer"},
            "time": {"type": "time"},

            # Circuits
            "circuit_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "circuit_location": {"type": "keyword"},
            "circuit_country": {"type": "keyword"},
            "circuit_coords": {"type": "geo_point"},

            # Drivers
            "driver_forename": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "driver_surname": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "driver_nationality": {"type": "keyword"},
            "driver_dob": {"type": "date", format: "yyyy-MM-dd"},
            "driver_code": {"type": "keyword"},

            # Constructors
            "constructor_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "constructor_nationality": {"type": "keyword"},

            # Race result
            "grid_position": {"type": "integer"},
            "finish_position": {"type": "integer"},  # null = DNF
            "points": {"type": "float"},
            "laps_completed": {"type": "integer"},
            "status": {"type": "keyword"},  # "Finished", "Retired", etc.
            "fastest_lap_rank": {"type": "integer"},
        }
    }
}