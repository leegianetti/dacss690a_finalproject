# Cambridge Service Requests: ETL Dashboard & Predictive Model

## Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline and interactive dashboard using the **City of Cambridge’s SeeClickFix (Commonwealth Connect)** data. It gives users — both **residents** and **city staff** — insight into the most common service requests submitted and provides predictive estimates of how long requests might take to resolve.

The system automatically pulls fresh data daily, processes it, trains a model, and updates a live Streamlit dashboard.

## Purpose

Residents report issues like potholes, graffiti, or missed trash pickup through the SeeClickFix app. This tool:
- Highlights the most common issues being reported.
- Displays request counts filtered by status and time range.
- Predicts the **estimated time-to-close** for new requests based on issue type, day, month, and time.

It helps city staff improve service delivery and gives the public visibility into government responsiveness using open data.

## Features

-Filter requests by date and status  
-Visualize the top 20 issue types by volume  
-Predict resolution time based on:
  - Issue category  
  - Weekday  
  - Month  
  - Hour of day  
-Map of reported issues with hover details  
-Auto-scheduled daily updates using Prefect  
-Lightweight, containerized app (runs locally via Docker)

## Data Source

- **Dataset:** [Commonwealth Connect Service Requests](https://data.cambridgema.gov/)
- **API:** Socrata Open Data API (SODA)  
- **CSV Endpoint:** `https://data.cambridgema.gov/resource/2z9k-mv9g.csv`
- **Documentation:** [Socrata SODA API Docs](https://dev.socrata.com/)
- **Access:** optional(but reccomended) app token stored in `.env`

## Data Transformation

The `transform.py` script processes and augments the raw service request data with the following steps:
1. **Datetime Parsing**: Converts datetime columns (e.g., ticket creation and closure times) into proper datetime objects.
2. **Feature Engineering**: Extracts additional features from datetime columns, such as:
   - Year, month, day, weekday, and hour of ticket creation and closure.
3. **String Formatting**: Creates a human-readable string version of the ticket creation timestamp for tooltips.
4. **Time-to-Close Calculation**: Computes the time taken to close each ticket (in hours) for requests with both creation and closure timestamps.
5. **Database Storage**: Saves the transformed data into the `service_requests_transformed` table in the SQLite database.

## Prediction Model

The `train_model.py` script trains a machine learning model to predict the estimated time to close service requests. Below are the details of the model:

1. **Model Type**:  
   - The model is a **Random Forest Regressor**, which is a robust and interpretable ensemble learning method.

2. **Features Used**:  
   - **Categorical Features**:
     - Issue category (e.g., "Missed Recycling Pickup").
     - Weekday of ticket creation (e.g., "Monday").
   - **Numerical Features**:
     - Month of ticket creation (e.g., January = 1).
     - Hour of ticket creation (e.g., 14 for 2 PM).

3. **Target Variable**:  
   - The model predicts the **time to close** a service request in hours, calculated as the difference between ticket closure and creation timestamps.

4. **Training Process**:  
   - The data is split into training and testing sets (80% training, 20% testing).
   - The model is trained on the training set and evaluated using the R² score on the test set.

5. **Model Storage**:  
   - The trained model is saved as a `.joblib` file (`time_to_close_model.joblib`) for use in the Streamlit dashboard.

6. **Usage in Dashboard**:  
   - Users can input features (e.g., issue category, weekday, month, hour) in the dashboard to get a prediction of the estimated time to close a new service request.

## Project Structure

```
your-project-folder/
├── .env                  # stores your API token securely
├── Dockerfile            # builds app container
├── docker-compose.yml    # launches Prefect and Streamlit services
├── extract.py            # downloads latest data from Socrata API
├── transform.py          # processes and augments data
├── train_model.py        # trains a predictive ML model
├── prefect_flow.py       # defines and schedules the ETL pipeline
├── app.py                # Streamlit app for UI & analysis
├── requirements.txt      # Python package dependencies
```

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-repo-link.git
cd your-repo-link
```

### 2. Create a `.env` File

Add your Socrata app token (get one [here](https://dev.socrata.com/register/)):

```
SODA_APP_TOKEN=your_token_here
```

### 3. Install Docker & Docker Compose

If not already installed:

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

### 4. Build and Run the App

```bash
docker-compose up --build
```

- This will launch:
  - `prefect_etl`: runs your ETL + model training script
  - `streamlit_app`: serves your dashboard at [http://localhost:8501](http://localhost:8501)

## Automation & Scheduling

- The ETL pipeline is orchestrated using **Prefect 2.x**
- Defined in `prefect_flow.py` with a daily schedule
- Automatically:
  - Extracts the latest data
  - Transforms it
  - Trains a machine learning model
- Scheduling is handled via Prefect’s `IntervalSchedule`

## Future Enhancements

- Add filters for geographic area (e.g., neighborhood or zip code)
- Connect to a scalable database like PostgreSQL
- Enhance the model using more predictive features (e.g., service department)
- Track year-over-year trends or seasonality
- Include detailed service performance reports for city leadership
- Export insights as PDF or CSV for public use
- Deploy the app to the cloud (e.g., AWS, Prefect Cloud)

## License

MIT License

## Maintainer

Lee Gianetti

