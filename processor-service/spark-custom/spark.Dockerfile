# spark-custom/spark.Dockerfile
FROM bitnami/spark:3.4

USER root
RUN apt-get update && apt-get install -y curl
USER 1001