import random
import string

import airflow
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

from team_league_etl_spark_scala_dag.settings import Settings

settings = Settings()

with airflow.DAG(
        "team_league_etl_spark_scala_dag",
        default_args=settings.dag_default_args,
        schedule_interval=None) as dag:
    batch_id_suffix = ''.join(random.choices(string.ascii_lowercase, k=5))

    create_team_league_batch = DataprocCreateBatchOperator(
        task_id="team_league_etl_spark_scala_job",
        project_id=settings.project_id,
        region=settings.team_stats_job_location,
        batch=settings.team_stats_job_config,
        batch_id=f"{settings.team_stats_job_batch_id}-{batch_id_suffix}"
    )

    move_file_to_cold = GCSToGCSOperator(
        task_id="move_file_to_cold",
        source_bucket=settings.team_stats_source_bucket,
        source_object=settings.team_stats_source_object,
        destination_bucket=settings.team_stats_dest_bucket,
        destination_object=settings.team_stats_dest_object,
        move_object=False
    )

    create_team_league_batch >> move_file_to_cold
