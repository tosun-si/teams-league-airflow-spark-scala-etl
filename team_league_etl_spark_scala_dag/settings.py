import os
from dataclasses import dataclass
from datetime import timedelta

from airflow.models import Variable
from airflow.utils.dates import days_ago

_variables = Variable.get("team_league_etl_spark_scala_dag", deserialize_json=True)
_current_dag_folder = _variables["dag_folder"]


@dataclass
class Settings:
    dag_default_args = {
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=5),
        "start_date": days_ago(1)
    }
    project_id = os.getenv("GCP_PROJECT")

    team_stats_job_config = _variables["team_stats_job_config"]
    team_stats_job_batch_id = _variables["team_stats_job_batch_id"]
    team_stats_job_location = _variables["team_stats_job_location"]

    team_stats_source_bucket = _variables["team_stats_source_bucket"]
    team_stats_source_object = _variables["team_stats_source_object"]
    team_stats_dest_bucket = _variables["team_stats_dest_bucket"]
    team_stats_dest_object = _variables["team_stats_dest_object"]

    variables = _variables
