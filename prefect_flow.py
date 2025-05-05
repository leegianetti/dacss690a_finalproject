from prefect import flow, task
from prefect_shell import ShellOperation
from datetime import datetime
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta

# Define a task to extract data
@task
def extract_data():
    """
    Executes the extract.py script to extract data.
    Returns the logs from the extraction process.
    """
    result = ShellOperation(
        commands=["python extract.py"],
        return_all=True
    ).run()
    return result

# Define a task to transform data
@task
def transform_data():
    """
    Executes the transform.py script to transform data.
    Returns the logs from the transformation process.
    """
    result = ShellOperation(
        commands=["python transform.py"],
        return_all=True
    ).run()
    return result

# Define a task to train a model
@task
def train_model():
    """
    Executes the train_model.py script to train a machine learning model.
    Returns the logs from the training process.
    """
    result = ShellOperation(
        commands=["python train_model.py"],
        return_all=True
    ).run()
    return result

# Define the main ETL flow
@flow(name="ETL + Model Training Pipeline", log_prints=True)
def etl_flow():
    """
    Orchestrates the ETL pipeline and model training process.
    Executes the extract, transform, and train tasks sequentially.
    """
    print("▶ Starting ETL pipeline run...")
    extract_logs = extract_data()  # Run the extract task
    transform_logs = transform_data()  # Run the transform task
    model_logs = train_model()  # Run the train task
    print("Pipeline completed.")

if __name__ == "__main__":
    # Run the flow directly if the script is executed
    etl_flow()

# Define a schedule (e.g., run every day)
schedule = IntervalSchedule(interval=timedelta(days=1))

# Create a deployment for the flow
deployment = Deployment.build_from_flow(
    flow=etl_flow,
    name="ETL + Model Training Deployment",
    schedule=schedule
)

if __name__ == "__main__":
    # Apply the deployment when the script is run
    deployment.apply()
    etl_flow()