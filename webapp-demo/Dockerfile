FROM python:3

COPY ./webapp-demo/requirements.txt .

RUN pip install -r requirements.txt && rm requirements.txt

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]