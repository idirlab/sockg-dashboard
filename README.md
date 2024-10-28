# SOCKG Dashboard

SOCKG Dashboard is an interactive web application designed for the SOCKG (Soil Organic Carbon Knowledge Graph). It provides visual display of key information as well as natural language querying the knowledge graph.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Key Components](#key-components)
- [License](#license)

## Features

- **Interactive Web Interface**: Built with Streamlit.
- **Data Visualization**: Visualize key classes such as Field, Experimental Unit, Treatment, ...
- **Natural Language Querying**: Query the Neo4j knowledge graph using natural language.

## Prerequisites

- Docker installed on your system (version 27.1.1 is tested)
- Since this project make use llama3:7b. 16GB of memory and a GPU available machine is recommmend

## Installation

This application is built and tested on Python 3.8. All dependencies are managed through Docker and a Python requirements.txt file.

To set up and run the application:

1. Clone the repository:
```
$ https://github.com/idirlab/sockg.git
```
2. Go into sockg-dashboard directory
```
$ cd sockg/sockg-dashboard/
```

3. Configure API key and Neo4j credentials:
- Navigate to `streamlit_app/.streamlit/`
- Create a file named `secrets.toml`
- Add the following configurations to `secrets.toml`:
```
  API_KEY = "<your gemini api key>"
  MODEL = "<llm model>"

  NEO4J_URI = "bolt://idir.uta.edu:7687"
  NEO4J_USERNAME = "<your sockg username>"    # Contact IDIR lab
  NEO4J_PASSWORD = "<your sockg password>"    # Contact IDIR lab
  MAP_BOX_API = <Your mapbox api key>         # Obtain for free on mapbox.com
```

4. Build and start the Docker containers:
```
docker compose up
```
This command builds the necessary Docker images and starts the containers as defined in the `docker-compose.yml` file.

## Usage

After the Docker build process completes and containers are running:

1. Open your web browser and go to `http://localhost:8501`
2. You will see the SOCKG Dashboard web interface.

Note: The application runs on port 8501 by default. Ensure this port is not in use by other applications on your system. Below is the example run of the app.

![Watch the Gif](./sockg_dashboard_demo.gif)
## Directory Structure
The project is organized as follows (assume sockg-dashboard is root):
```
/sockg-dashboard
├── streamlit_app/        # Source code for the application
│   ├── .streamlit        # Configuration directory (e.g., secrets.toml)
│   ├── collected_datas/  # User ratings for question-cypher pairs
│   │   └── ....json
│   ├── componets/        # Reusable visualization components
│   |   └── ...
|   ├── models/           # LangChain objects for LLMs and embeddings
|   ├── neo4j-connector   # Neo4j driver initialization
|   ├── pages/            # Streamlit pages (e.g., /Fields, /Treatment)
|   ├── templates/        # LLM prompt templates
|   └── tools/            # LangChain tools for few-shot (RAG) agents
|
├── Docker-compose.yaml   # Docker Compose specification
└── README.md             # Project overview
```

## Keys Components
1. Front End: 
  * The app is built using [Streamlit](https://streamlit.io/) framework, and organized into [subpages](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app)
  * 3D graph is generated using [Plotly](https://plotly.com/python/) and rendered by streamlit.
  * Geospatial map is generated using [Pydeck](https://deckgl.readthedocs.io/en/latest/) and rendered using streamlit.

  2. Back End:
  Natural Language to Cypher is a subpage allows users to query the knowledge graph using natural language.
  * Powered by LLaMA3(for Embedding) and Gemini(for inference) as a RAG (retrieval-augmented generation) agent with dynamic few-shot learning.
  * Uses google gemini as llm model for Cypher generation and Llama3 for sentence embedding.
  * Few-shot examples, including question-Cypher-query pairs, are stored in a Chrono in-memory database for dynamic selection using sentence embedding.