# search-service
A fast search engine built with Python


Simple Search Engine API

Overview:
This repository contains the implementation of a simple search engine API as part of a backend software engineer assignment. The goal of this project is to build an API that allows querying a data source and returning matching records efficiently.

Purpose:
The main objective of this assignment is to create a lightweight and performant search engine API that meets the following requirements:

Expose a /search endpoint to query the data source.

Return paginated results quickly, ideally under 100ms.

Implemented in the latest stable version of Python.


Setup and Installation

Clone the repository:
git clone 'repository-url'


Navigate to the project directory on your Terminal:
cd 'project-directory'


Activate the env:
source .venv/bin/activate


Run the application:
bash start.sh


Bonus Goals:
Design Notes: In the README, we discuss various alternative approaches considered for building the search engine.

The approach I used is a lightweight, embedded search engine built on SQLite with Full-Text Search (FTS5). In other words, it’s often referred to as an "embedded FTS search" approach.

Alternative Approaches:

1. Elasticsearch/OpenSearch: More scalable for large datasets, offers advanced search features and analytics, but requires more infrastructure and maintenance.

2. PostgreSQL with Full-Text Search: Offers robust search capabilities with built-in indexing, but can be heavier to set up and manage compared to SQLite.

3. Custom Inverted Index: Building a custom inverted index in memory can give you fine-grained control but can be complex and memory-intensive.

   

Data Insights: We explain strategies to optimize performance and reduce latency to 30ms.

Submission:
The project is deployed and publicly accessible.
