#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def detect_timestamp_col(cols):
    names = ['timestamp','datetime','time','date','ts']
    for c in names:
        if c in cols:
            return c
    for c in cols:
        if 'time' in c.lower() or 'date' in c.lower():
            return c
    return None

def ingest_csvs(data_dir=DATA_DIR):
    csv_files = sorted(data_dir.glob("*.csv"))
    frames = []
    issues = []

    for f in csv_files:
        try:
            df = pd.read_csv(f, on_bad_lines='skip')
        except Exception as e:
            logging.error(f"Error reading {f}: {e}")
            issues.append((f.name, str(e)))
            continue

        building = None
        for col in ('building','site','name'):
            if col in df.columns:
                building = df[col].iloc[0]
                break
        if building is None:
            building = f.stem.split('_')[0]

        ts_col = detect_timestamp_col(df.columns)
        if ts_col is None:
            issues.append((f.name, "NoTimestamp"))
            continue

        kwh_col = None
        for col in ('kwh','kwh_consumed','consumption','energy','value'):
            if col in df.columns:
                kwh_col = col
                break
        if kwh_col is None:
            nums = df.select_dtypes(include=[np.number]).columns.tolist()
            nums = [c for c in nums if c != ts_col]
            if nums:
                kwh_col = nums[0]
            else:
                issues.append((f.name, "NoKwh"))
                continue

        temp = df[[ts_col, kwh_col]].copy()
        temp.columns = ['timestamp','kwh']
        temp['building'] = building

        temp['timestamp'] = pd.to_datetime(temp['timestamp'], errors='coerce')
        temp = temp.dropna(subset=['timestamp'])

        temp['kwh'] = pd.to_numeric(temp['kwh'], errors='coerce')
        temp = temp.dropna(subset=['kwh'])

        frames.append(temp)

    if frames:
        out = pd.concat(frames, ignore_index=True).sort_values('timestamp')
    else:
        out = pd.DataFrame(columns=['timestamp','kwh','building'])

    if issues:
        with open(OUTPUT_DIR / "ingest_issues.log", "w") as f:
            for x in issues:
                f.write(f"{x[0]}\t{x[1]}\n")

    return out

def calculate_daily_totals(df):
    if df.empty:
        return pd.DataFrame()
    d = df.set_index('timestamp')
    return d.groupby('building').resample('D').sum().reset_index()

def calculate_weekly_aggregates(df):
    if df.empty:
        return pd.DataFrame()
    d = df.set_index('timestamp')
    w = d.groupby('building').resample('W').agg({'kwh':['sum','mean']})
    w.columns = ['weekly_sum','weekly_mean']
    return w.reset_index()

def building_wise_summary(df):
    if df.empty:
        return pd.DataFrame()
    return df.groupby('building').agg(
        mean_kwh=('kwh','mean'),
        min_kwh=('kwh','min'),
        max_kwh=('kwh','max'),
        total_kwh=('kwh','sum'),
        samples=('kwh','count')
    ).reset_index()

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = pd.to_datetime(timestamp)
        self.kwh = float(kwh)

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, timestamp, kwh):
        self.meter_readings.append(MeterReading(timestamp, kwh))

    def to_dataframe(self):
        if not self.meter_readings:
            return pd.DataFrame(columns=['timestamp','kwh','building'])
        df = pd.DataFrame([(r.timestamp, r.kwh) for r in self.meter_readings],
                          columns=['timestamp','kwh'])
        df['building'] = self.name
        return df

    def calculate_total_consumption(self):
        df = self.to_dataframe()
        return df['kwh'].sum()

    def generate_report_text(self):
        df = self.to_dataframe()
        if df.empty:
            return f"{self.name}: no data"
        total = df['kwh'].sum()
        mean = df['kwh'].mean()
        peak_row = df.loc[df['kwh'].idxmax()]
        peak_time = peak_row['timestamp']
        peak_val = peak_row['kwh']
        return f"{self.name}: total={total:.2f} kWh, mean={mean:.2f}, peak={peak_val:.2f} at {peak_time}"

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def ingest_dataframe(self, df):
        for _, row in df.iterrows():
            name = row['building']
            if name not in self.buildings:
                self.buildings[name] = Building(name)
            self.buildings[name].add_reading(row['timestamp'], row['kwh'])

    def generate_all_reports(self):
        return {name: b.generate_report_text() for name, b in self.buildings.items()}

def plot_dashboard(df_daily, df_weekly, df_combined):
    fig, axes = plt.subplots(3,1, figsize=(12, 14), constrained_layout=True)

    ax = axes[0]
    for b, g in df_daily.groupby('building'):
        ax.plot(g['timestamp'], g['kwh'], label=b)
    ax.set_title('Daily Consumption')
    ax.set_xlabel('Date')
    ax.set_ylabel('kWh')
    ax.legend()

    ax = axes[1]
    if not df_weekly.empty:
        avg = df_weekly.groupby('building')['weekly_mean'].mean().sort_values(ascending=False)
        ax.bar(avg.index, avg.values)
    ax.set_title('Average Weekly Usage')
    ax.set_ylabel('kWh')
    ax.tick_params(axis='x', rotation=45)

    ax = axes[2]
    if not df_combined.empty:
        df_h = df_combined.set_index('timestamp').groupby('building').resample('H')['kwh'].sum().reset_index()
        for b, g in df_h.groupby('building'):
            ax.scatter(g['timestamp'], g['kwh'], s=10, alpha=0.6, label=b)
    ax.set_title('Hourly Usage (Scatter)')
    ax.set_ylabel('kWh')
    ax.legend()

    fig.suptitle("Campus Energy Dashboard")
    path = OUTPUT_DIR / "dashboard.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path

def compose_summary(df, building_summary_df, weekly_df):
    if df.empty or building_summary_df.empty:
        return "No data available."

    total = df['kwh'].sum()
    top = building_summary_df.sort_values('total_kwh', ascending=False).iloc[0]
    top_name = top['building']
    top_total = top['total_kwh']

    hourly = df.set_index('timestamp').resample('H')['kwh'].sum().reset_index()
    peak = hourly.loc[hourly['kwh'].idxmax()]
    peak_time = peak['timestamp']
    peak_val = peak['kwh']

    summary = [
        f"Campus Energy Summary ({datetime.utcnow().isoformat()}Z)",
        "-"*50,
        f"Total campus usage: {total:.2f} kWh",
        f"Top building: {top_name} ({top_total:.2f} kWh)",
        f"Peak hour: {peak_val:.2f} kWh at {peak_time}",
        "",
        "General Notes:",
        "- Highest building may need an energy check.",
        "- Review operations during peak hour.",
        "- Dashboard saved as dashboard.png"
    ]
    return "\n".join(summary)

def write_outputs(df_combined, building_summary_df, summary_text):
    df_combined.to_csv(OUTPUT_DIR / "cleaned_energy_data.csv", index=False)
    building_summary_df.to_csv(OUTPUT_DIR / "building_summary.csv", index=False)
    with open(OUTPUT_DIR / "summary.txt", "w") as f:
        f.write(summary_text)

def main():
    df = ingest_csvs()

    if df.empty:
        write_outputs(df, pd.DataFrame(), "No data available.")
        return

    df_daily = calculate_daily_totals(df)
    df_weekly = calculate_weekly_aggregates(df)
    building_summary_df = building_wise_summary(df)

    manager = BuildingManager()
    manager.ingest_dataframe(df)
    for report in manager.generate_all_reports().values():
        logging.info(report)

    dashboard_path = plot_dashboard(df_daily, df_weekly, df)

    summary_text = compose_summary(df, building_summary_df, df_weekly)
    write_outputs(df, building_summary_df, summary_text)

    print(summary_text)
    print(f"Dashboard saved at: {dashboard_path.resolve()}")

if __name__ == "__main__":
    main()
