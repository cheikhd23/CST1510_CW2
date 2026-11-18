"""
Beneath - Week 8: Earthquake data collection
Name: Cheikh Ahmed Tidiane Dione
Module: CST1510 Coursework 2

Based on the Week 8 lab template, using its earthquake settings.
Additional output shows the number of rows before and after cleaning.

Run: python3 fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests


# API settings supplied in the lab.
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
PARAMS = {
    "format": "geojson",
    "minmagnitude": 2.5,
    "limit": 500
}
RECORDS_KEY = "features"

# Rename the API fields to readable column names.
RENAME = {
    "properties_mag": "mag",
    "properties_place": "place",
    "properties_time": "time",
    "properties_magType": "mag_type",
    "properties_sig": "significance",
    "properties_tsunami": "tsunami"
}

KEEP = [
    "time",
    "place",
    "mag",
    "mag_type",
    "depth_km",
    "significance",
    "tsunami"
]

MUST_HAVE = ["mag"]

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


def get_data(url, params):
    """Request API data. Return JSON, or None if the request fails."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Extract the records and flatten them into a pandas table."""
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Rename fields, prepare earthquake values and clean the table."""
    rows_before = len(df)

    df = df.rename(columns=RENAME)

    # Depth is the third value in the coordinates list.
    df["depth_km"] = df["geometry_coordinates"].apply(
        lambda coords: coords[2]
    )

    # Convert the timestamp from milliseconds to readable text.
    df["time"] = pd.to_datetime(
        df["time"], unit="ms"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    df = df[KEEP]
    df = df.dropna(subset=MUST_HAVE)

    print("\nBENEATH | Cleaning summary")
    print("Rows before cleaning:", rows_before)
    print("Rows after cleaning:", len(df))
    print("Rows removed:", rows_before - len(df))
    print("Columns retained:", len(df.columns))

    return df


def save_data(df, path):
    """Create the data folder if needed and save the CSV."""
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} rows to {path}")


if __name__ == "__main__":
    print("BENEATH | Fetching earthquake data")

    data = get_data(URL, PARAMS)

    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)

        print("\nPreview:")
        print(table.head())

        save_data(table, RAW_FILE)