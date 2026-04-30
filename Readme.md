# F1 Elasticsearch
A practical of Elasticsearch using the Formula 1 Word Championship dataset (1950 - 2024).
The project indexes races results, driver data, constructor data and curcuit information in into elasticsarch
and demonstrates core features such as full-text-search, fuzzy search, filtering, 
bool queries and aggregations. A Kibana dashboard provides visual insights into the data.

## Requierments
- **Dataset:** Download the dataset from Kaggle https://www.kaggle.com/datasets/jtrotman/formula-1-race-data
- **Elasticsearch instance**
- **Kibana instance**

## Installation
To setup an elasticsarch instance with kibana for viusalisation - run the docker-compose script in this repository
```jsunicoderegexp
docker-compose.yml
```
1) Run command in terminal
```bash
docker compose up -d
```
2) Run ```docker ps``` to make sure that the elasticsarch and the kibana container is running
```bash
fabiankopf@MacBook-Pro-Fabian ElasticSearch % docker ps
CONTAINER ID   IMAGE                 COMMAND                  CREATED          STATUS          PORTS                                         NAMES
xxx   kibana:9.3.1          "/bin/tini -- /usr/l…"   11 seconds ago   Up 10 seconds   0.0.0.0:5601->5601/tcp, [::]:5601->5601/tcp   kibana
xxx   elasticsearch:9.3.1   "/bin/tini -- /usr/l…"   11 seconds ago   Up 10 seconds   0.0.0.0:9200->9200/tcp, [::]:9200->9200/tcp   elasticsearch
```
3)The Elasitcsearch instance is available at http://localhost:9200 and the Kibana instance is available at http://localhost:5601