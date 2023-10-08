import os
import pickle
import json
import calendar
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import starlette.status as status

app = FastAPI(title="Predicting Delivery Times")

app.mount("/static", StaticFiles(directory="static"), name="static")

class Logistics(BaseModel):
    distance: float
    dow_created_time: int
    hour_created_time: int
    suggested_deli_supplier: int
    destination_address_type: int
    destination_district: float
    seller_id: int
    suggested_pickup_supplier: float
    departure_region: float
    route: float
    datetime_created_at: datetime

def predicting(original_test, processed_test, model):
    y_pred = model.predict(processed_test)
    final_y_pred = post_processing(original_test, y_pred)

    return final_y_pred

def post_processing(df, y_pred):
        def round_datetime(x):
            return datetime(year=x.year, month=x.month, day=x.day, hour=23, minute=59, second=59)

        def round_deli(row):
            delta = row['round_deli_time'] - row['datetime_created_at']
            value = delta.total_seconds() / 3600 / 24
            return value

        y_pred = y_pred / 24.0

        df["y_pred"] = y_pred
        df["deli_time"] = df.apply(lambda x: x["datetime_created_at"] +
                             timedelta(days=x["y_pred"]), axis="columns")
        df["round_deli_time"] = df["deli_time"].apply(round_datetime)

        df['dow'] = df["round_deli_time"].apply(lambda x: x.weekday())
        df['dow_old_name'] = df["dow"].apply(lambda x: calendar.day_name[x])

        df["round_deli_time"] = df.apply(lambda row: apply_office(row, "round_deli_time"), axis=1)
        df["round_deli_time"] = df.apply(lambda row: apply_home(row, "round_deli_time"), axis=1)

        df['dow_new'] = df["round_deli_time"].apply(lambda x: x.weekday())
        df['dow_new_name'] = df["dow_new"].apply(lambda x: calendar.day_name[x])
        df["round_deli"] = df.apply(round_deli, axis="columns")
        df["round_etd"] = df["round_deli_time"].apply(lambda x: datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
        total_adjusted = np.sum((df["round_deli"] - y_pred) >= 1)

        return df["round_deli"].values, df["round_deli_time"].values

def apply_office(row, adjust_column):
    if row["destination_address_type"] == 1:
        if row["dow"] == 5:
            return row[adjust_column] + timedelta(days=2)
        elif row["dow"] == 6:
            return row[adjust_column] + timedelta(days=1)
        else:
            return row[adjust_column]
    else:
        return row[adjust_column]

def apply_home(row, adjust_column):
    if row["destination_address_type"] == 0:
        if row["dow"] == 6:
            return row[adjust_column] + timedelta(days=1)
        else:
            return row[adjust_column]
    else:
        return row[adjust_column]
    

@app.on_event("startup")
def load_reg():
    with open("/app/logistic_model.pkl", "rb") as file:
        global reg 
        reg = pickle.load(file)

@app.get("/")
def home():
    #return "Welcome to our systems!"
    return RedirectResponse(url="/static/products.html", status_code=status.HTTP_302_FOUND)


@app.post("/predict")
def predict(logis: Logistics):

    results_folder = 'Predictions'
    os.makedirs(results_folder, exist_ok=True)
    output_json_path = os.path.join(results_folder, "prediction.json")

    data_point = np.array(
        [
            [
                logis.distance,
                logis.dow_created_time,
                logis.hour_created_time,
                logis.suggested_deli_supplier,
                logis.destination_address_type,
                logis.destination_district,
                logis.seller_id,
                logis.suggested_pickup_supplier,
                logis.departure_region,
                logis.route,
            ]
        ]
    )

    df_post = pd.DataFrame(
        {
            'datetime_created_at': [logis.datetime_created_at],
            'destination_address_type': [logis.destination_address_type]
        }
    )

    predicted_delivery_leadtime, predicted_shipping_date = predicting(df_post, data_point, reg)

    output = pd.DataFrame({'predicted_shipping_date': predicted_shipping_date})
    output['predicted_shipping_date'] = output['predicted_shipping_date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    output_dict = output.to_dict(orient="records")[0]
    return output_dict
    # encoded_data = jsonable_encoder(output_dict)

    # with open(output_json_path, "w") as json_file:
    #     json.dump(encoded_data, json_file, indent=2)

    # return "Predicting and saved result successfully!"
