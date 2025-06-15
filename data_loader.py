import pandas as pd
from pymongo import MongoClient
from datetime import datetime

MONGODB_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URL)
db = client["store_monitoring"]

def load_status(path):
    df = pd.read_csv(path)
    df['timestamp_utc'] = df['timestamp_utc'].apply(lambda x: x if x.endswith(" UTC") else f"{x} UTC")
    db["status"].delete_many({})
    db["status"].insert_many(df.to_dict(orient="records"))

def load_business_hours(path):
    df = pd.read_csv(path)
    df = df.fillna("")
    df["dayOfWeek"] = df["dayOfWeek"].astype(int)
    db["business_hours"].delete_many({})
    db["business_hours"].insert_many(df.to_dict(orient="records"))

def load_timezones(path):
    df = pd.read_csv(path)
    db["timezones"].delete_many({})
    db["timezones"].insert_many(df.to_dict(orient="records"))

if __name__ == "__main__":
    # Place CSVs in ./data/
    load_status("./data/store_status.csv")
    load_business_hours("./data/menu_hours.csv")
    load_timezones("./data/timezones.csv")
    print("Data loaded.")