from elasticsearch import Elasticsearch, helpers
import pandas as pd

ES_HOST = 'http://localhost:9200'
ES_INDEX = 'f1'
DATASET_PATH = "../f1_dataset"

"""
text ... for fields which should be searched inside. So texts like "Monaco Grand Prix" can be searched by using the keyword "monaco"
keyword ... for fields you want to filter or group by exactly (e.g. group by country)
text + keyword ... on some fields i want both functionality - to search them fuzzily and aggregate them by exact values
integer/float ... numeric fields, enables range queries and numeric aggregations
date ... used that elasticsearch understands chronological order and enables filter by time ranges
geo_point ... stores lat/lon coordinates - with this type visualizations in kibana can be created
"""
MAPPING = {
    "mappings": {
        "properties": {
            # Race
            "race_id": {"type": "integer"},
            "race_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "season": {"type": "integer"},
            "round": {"type": "integer"},
            "race_date": {"type": "date", "format": "yyyy-MM-dd"},

            # Circuits
            "circuit_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "circuit_location": {"type": "keyword"},
            "circuit_country": {"type": "keyword"},
            "circuit_coords": {"type": "geo_point"},

            # Drivers
            "driver_id": {"type": "integer"},
            "driver_number": {"type": "integer"},
            "driver_forename": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "driver_surname": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "driver_nationality": {"type": "keyword"},
            "driver_dob": {"type": "date", "format": "yyyy-MM-dd"},
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


def load_csv(path: str) -> dict:
    """Load all relevant csv files into dataframes"""
    return {
        "races": pd.read_csv(f"{path}/races.csv"),
        "results": pd.read_csv(f"{path}/results.csv"),
        "drivers": pd.read_csv(f"{path}/drivers.csv"),
        "constructors": pd.read_csv(f"{path}/constructors.csv"),
        "circuits": pd.read_csv(f"{path}/circuits.csv"),
        "status": pd.read_csv(f"{path}/status.csv")
    }


def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_str(val):
    try:
        return str(val)
    except (ValueError, TypeError):
        return None


def build_document(dfs: dict):
    """
    Merge all csv's into a flat list of documents - one document per race result.
    This is the denormalization step: ElasticSearch works best with flat documents rather than nested relational tables.
    """

    df = dfs["results"].merge(dfs["races"], on="raceId", suffixes=("", "_race"))
    df = df.merge(dfs["drivers"], on="driverId", suffixes=("", "_driver"))
    df = df.merge(dfs["constructors"], on="constructorId", suffixes=("", "_constructor"))
    df = df.merge(dfs["circuits"], on="circuitId", suffixes=("", "_circuit"))
    df = df.merge(dfs["status"], on="statusId", suffixes=("", "_status"))
    df.replace("\\N", None, inplace=True)

    documents = []
    for _, row in df.iterrows():
        try:
            coords = {"lat": float(row["lat"]), "lon": float(row["lng"])}
        except (TypeError, ValueError):
            coords = None

        doc = {
            # Race
            "race_id": safe_int(row.get("raceId")),
            "race_name": safe_str(row.get("name")),
            "season": safe_int(row.get("year")),
            "round": safe_int(row.get("round")),
            "race_date": safe_str(row.get("date")),

            # Circuits
            "circuit_name": safe_str(row.get("name_circuit")),
            "circuit_location": safe_str(row.get("location")),
            "circuit_country": safe_str(row.get("country")),
            "circuit_coords": coords,

            # Driver
            "driver_id": safe_int(row.get("driverId")),
            "driver_number": safe_int(row.get("number")),
            "driver_forename": safe_str(row.get("forename")),
            "driver_surname": safe_str(row.get("surname")),
            "driver_nationality": safe_str(row.get("nationality")),
            "driver_dob": safe_str(row.get("dob")),
            "driver_code": safe_str(row.get("code")),

            # Constructor
            "constructor_name": safe_str(row.get("name_constructor")),
            "constructor_nationality": safe_str(row.get("nationality_constructor")),

            # Race result
            "grid_position": safe_int(row.get("grid")),
            "finish_position": safe_int(row.get("positionOrder")),
            "points": safe_float(row.get("points")),
            "laps_completed": safe_int(row.get("laps")),
            "status": safe_str(row.get("status")),
            "fastest_lap_rank": safe_int(row.get("rank")),
        }

        documents.append(doc)
    print(f"Built {len(documents):,} documents")
    return documents


def create_index(es: Elasticsearch):
    """Delete existing index and create a fresh one with the mapping"""
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
    es.indices.create(index=ES_INDEX, body=MAPPING)


def bulk_index(es: Elasticsearch, documents: list):
    """Bulk index all documents into ElasticSearch"""
    actions = [{"_index": ES_INDEX, "_source": doc}
               for doc in documents]

    success, errors = helpers.bulk(es, actions, chunk_size=500, raise_on_error=False)
    if errors:
        print(f"Errors: {len(errors)} documents failed")
        for e in errors:
            print(e)

def main():
    es = Elasticsearch(hosts=ES_HOST)
    if not es.ping():
        print("Elasticsearch is not reachable")
        return

    info = es.info()
    print(f"Connected! ES Version: {info['version']['number']}")

    dfs = load_csv(DATASET_PATH)
    documents = build_document(dfs)
    create_index(es)
    bulk_index(es, documents)

    es.indices.refresh(index=ES_INDEX)
    count = es.count(index=ES_INDEX)["count"]
    print(f"\nDone! Index '{ES_INDEX}' contains {count:,} documents.")

if __name__ == "__main__":
    main()