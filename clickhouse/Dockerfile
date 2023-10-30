FROM clickhouse/clickhouse-server:22.2

COPY ./clickhouse/* /backups

RUN clickhouse-client

RUN pip install -r requirements.txt && rm requirements.txt

EXPOSE 8123

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]