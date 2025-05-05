from prefect import Flow
from prefect.schedules import CronSchedule

schedule = CronSchedule("0 0 * * *")  # Runs daily at midnight

with Flow("daily-flow", schedule=schedule) as flow:
    pass  # Placeholder to avoid "Expected indented block" error
