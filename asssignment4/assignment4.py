import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("weather.csv")

print(df.head())
print(df.info())
print(df.describe())

df["date"] = pd.to_datetime(df["date"])
df["rainfall"] = df["rainfall"].fillna(0)
df["humidity"] = df["humidity"].fillna(df["humidity"].mean())

df = df[["date", "temperature", "rainfall", "humidity"]]

df = df.set_index("date")

t_mean = np.mean(df["temperature"])
t_min = np.min(df["temperature"])
t_max = np.max(df["temperature"])
t_std = np.std(df["temperature"])

print(t_mean, t_min, t_max, t_std)

monthly = df.resample("M").mean()
yearly = df.resample("Y").mean()

print(monthly.head())
print(yearly)

plt.plot(df.index, df["temperature"])
plt.title("Daily Temperature")
plt.savefig("temp_line.png")
plt.show()

rain = df["rainfall"].resample("M").sum()
rain.plot(kind="bar")
plt.title("Monthly Rainfall")
plt.savefig("rain_bar.png")
plt.show()

plt.scatter(df["humidity"], df["temperature"])
plt.title("Humidity vs Temperature")
plt.savefig("hum_vs_temp.png")
plt.show()

plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.plot(df.index, df["temperature"])
plt.title("Temp")
plt.subplot(1,2,2)
plt.bar(rain.index, rain)
plt.title("Rain")
plt.savefig("combined.png")
plt.show()

m_group = df.groupby(df.index.month).mean()
print(m_group)

def season(x):
    if x in [12,1,2]:
        return "Winter"
    if x in [3,4,5]:
        return "Summer"
    if x in [6,7,8]:
        return "Monsoon"
    return "Post-Monsoon"

df["season"] = df.index.month.map(season)
s_group = df.groupby("season").mean()
print(s_group)

df.to_csv("cleaned_weather.csv")

with open("report.txt","w") as f:
    f.write("Weather Report\n")
    f.write("Mean Temp: " + str(t_mean))
