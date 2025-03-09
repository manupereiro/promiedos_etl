# My Airflow Project

This project is an Apache Airflow setup that includes a DAG for running a scraper bot. The scraper bot is scheduled to run at a specific time each day and saves the generated CSV file to Google Cloud Storage.

## Project Structure

```
my-airflow-project
├── dags
│   └── scraper_dag.py       # Contains the DAG definition for the scraper bot
├── plugins
│   └── __init__.py          # Initializes the plugins directory for custom operators, sensors, or hooks
├── requirements.txt          # Lists the dependencies required for the project
└── README.md                 # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd my-airflow-project
   ```

2. **Install dependencies**:
   Ensure you have Python and pip installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Configure Airflow**:
   Set up your Airflow environment by following the official Airflow documentation. Make sure to configure the connection to Google Cloud Storage.

4. **Start Airflow**:
   Initialize the database and start the web server and scheduler:
   ```
   airflow db init
   airflow webserver --port 8080
   airflow scheduler
   ```

## Usage

The scraper bot is scheduled to run daily at the specified time in the `scraper_dag.py` file. You can monitor the execution and logs through the Airflow web interface.

## Dependencies

This project requires the following libraries:
- Apache Airflow
- Google Cloud Storage client library
- Web scraping libraries (e.g., BeautifulSoup, requests)

Make sure to check the `requirements.txt` file for the complete list of dependencies.