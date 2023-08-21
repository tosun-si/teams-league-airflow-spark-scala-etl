# teams-league-airflow-cloudrun-etl

This project shows a real world use case with ETL batch pipeline using Cloud Storage, Scala Spark with Dataproc 
Serverless and BigQuery orchestrated by Cloud Composer / Airflow

![etl_batch_pipeline_composer_spark_scala_serverless_bq.png](diagram%2Fetl_batch_pipeline_composer_spark_scala_serverless_bq.png)

## Set env vars in your Shell

```shell
# Common
export PROJECT_ID={{project}}
export LOCATION={{location}}

# Deploy Spark job
export LOCAL_JAR_PATH=target/scala-2.13/team-league-airflow-spark-etl-assembly-0.1.0-SNAPSHOT.jar
export GCS_JARS_PATH=gs://mazlum_dev/spark/jars

# Deploy DAG in Composer
export DAG_FOLDER=team_league_etl_spark_scala_dag
export COMPOSER_ENVIRONMENT=dev-composer-env
export CONFIG_FOLDER_NAME=config
export ENV=dev
```

## Enable private access subnet

Dataproc Serverless requires Google Private Access to be enabled in the regional subnet where you run your Spark workloads since Spark drivers and executors require private IP addresses.

Enable Google Private Access on the default subnet in your selected region.

```bash
gcloud compute networks subnets \
  update default \
  --region=europe-west1 \
  --enable-private-ip-google-access
```

Verify that Google Private Access is enabled. The output should be True.

```bash
gcloud compute networks subnets \
    describe default \
    --region=europe-west1 \
    --format="get(privateIpGoogleAccess)"
```

Create a Persistent History Server

The Spark UI provides insights into Spark batch workloads. You can create a single-node Dataproc persistent history server that hosts the Spark UI and provides access to the history of completed Dataproc Serverless workloads.

Set a name for your persistent history server.

```bash
PHS_CLUSTER_NAME=gb-spark-job-history
```

```bash
gcloud dataproc clusters create \
    ${PHS_CLUSTER_NAME} \
    --region=europe-west1 \
    --single-node \
    --enable-component-gateway \
    --properties=spark:spark.history.fs.logDirectory='gs://mazlum_dev/phs/*/spark-job-history'
```

## Generate the fat jar with sbt and the assembly plugin

```bash
sbt assembly
```

## Copy the fat jar in the bucket

```bash
gcloud alpha storage cp teams-league-spark-scala-assembly-0.1.0-SNAPSHOT.jar gs://mazlum_dev/spark/jars
```

## Run the Spark job locally :

```bash
gcloud dataproc batches submit spark \
    --project=gb-poc-373711 \
    --region=europe-west1 \
    --service-account=sa-dataproc-serverless-dev@gb-poc-373711.iam.gserviceaccount.com \
    --jars="gs://mazlum_dev/spark/jars/teams-league-spark-scala-assembly-0.1.0-SNAPSHOT.jar" \
    --class="fr.groupbees.application.TeamLeagueApp" \
    --history-server-cluster=projects/gb-poc-373711/regions/europe-west1/clusters/gb-spark-job-history \
    -- gs://mazlum_dev/hot/etl/spark/input_teams_stats_raw.json gs://mazlum_dev/hot/etl/spark/input_team_slogans.json mazlum_test team_stat 
```

## Deploy the Spark job with Cloud Build from local machine

```shell
gcloud builds submit \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --config deploy-spark-job.yaml \
    --substitutions _LOCAL_JAR_PATH="$LOCAL_JAR_PATH",_GCS_JARS_PATH="$GCS_JARS_PATH" \
    --verbosity="debug" .
```

## Deploy the Spark job with Cloud Build manual trigger on Github repository

```bash
gcloud beta builds triggers create manual \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="deploy-spark-scala-job" \
    --repo="https://github.com/tosun-si/teams-league-spark-scala-dataproc-serverless" \
    --repo-type="GITHUB" \
    --branch="main" \
    --build-config="deploy-spark-job.yaml" \
    --substitutions _LOCAL_JAR_PATH="$LOCAL_JAR_PATH",_GCS_JARS_PATH="$GCS_JARS_PATH" \
    --verbosity="debug"
```

## Deploy the Airflow DAG in Composer with Cloud Build from the local machine

```shell
gcloud builds submit \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --config deploy-airflow-dag.yaml \
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT",_CONFIG_FOLDER_NAME="$CONFIG_FOLDER_NAME",_ENV="$ENV" \
    --verbosity="debug" .
```

## Deploy the Airflow DAG in Composer with a Cloud Build manual trigger :

```bash
gcloud beta builds triggers create manual \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="deploy-airflow-dag-spark-scala-elt-team-stats" \
    --repo="https://github.com/tosun-si/teams-league-airflow-spark-scala-etl" \
    --repo-type="GITHUB" \
    --branch="main" \
    --build-config="deploy-airflow-dag.yaml" \
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT",_CONFIG_FOLDER_NAME="$CONFIG_FOLDER_NAME",_ENV="$ENV" \
    --verbosity="debug"
```

