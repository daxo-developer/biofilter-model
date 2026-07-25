import pandas as pd
import requests
import os
import numpy as np

def load_usgs_data(site='01646500', parameter='00631',
                   start='2023-01-01', end='2023-12-31'):
    """Load nitrate data from USGS WaterData (RDB format)."""
    url = (f"https://waterservices.usgs.gov/nwis/iv/"
           f"?sites={site}&parameterCd={parameter}"
           f"&startDT={start}&endDT={end}&format=rdb")
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"USGS request failed: {response.status_code}")

    lines = response.text.splitlines()
    data_lines = [line for line in lines if not line.startswith('#')]
    if len(data_lines) < 2:
        raise ValueError("No data returned from USGS")

    header = data_lines[0].split('\t')  # split by tab
    datetime_col = 'datetime'
    value_col = f'{parameter}_00000'
    if datetime_col not in header or value_col not in header:
        raise ValueError(f"Required columns not found: {header}")

    datetime_idx = header.index(datetime_col)
    value_idx = header.index(value_col)

    dates, values = [], []
    for line in data_lines[1:]:
        parts = line.split('\t')
        if len(parts) > max(datetime_idx, value_idx):
            try:
                dt = pd.to_datetime(parts[datetime_idx])
                val = float(parts[value_idx])
                dates.append(dt)
                values.append(val)
            except (ValueError, IndexError):
                continue

    if not dates:
        raise ValueError("No valid numeric data parsed")

    df_raw = pd.DataFrame({'datetime': dates, 'value': values})
    df_raw = df_raw.dropna().sort_values('datetime').reset_index(drop=True)

    time0 = df_raw['datetime'].min()
    df_raw['time_days'] = (df_raw['datetime'] - time0).dt.total_seconds() / 86400.0
    df_raw['inlet'] = df_raw['value']

    np.random.seed(42)
    shift = 2
    df_raw['outlet'] = df_raw['inlet'].shift(int(shift * 24))
    df_raw['outlet'].fillna(df_raw['inlet'], inplace=True)
    df_raw['outlet'] = df_raw['outlet'] + 0.02 * np.random.randn(len(df_raw))

    return df_raw[['time_days', 'inlet', 'outlet']]

def load_local_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")
    df = pd.read_csv(filepath)
    required = ['time_days', 'inlet', 'outlet']
    if not all(col in df.columns for col in required):
        raise ValueError("CSV must contain columns: time_days, inlet, outlet")
    return df
