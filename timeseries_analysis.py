from pathlib import Path
import datetime as dt
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose, STL, MSTL

stl_kwargs = {"seasonal_deg": 0,
              "trend_deg": 0}
sensor = "SEN"
workdir = Path().absolute().parent
indir = workdir / "input" / "satellite"
ts_file = indir / "agramon_ANT.csv"
start_date = dt.datetime(2016, 10, 1)
end_date = dt.datetime(2024, 10, 1)
data = pd.read_csv(ts_file, sep=";")

data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")
data.loc[:, "platform"] = data["platform"].str.slice(start=0, stop=3)
# valid = np.isin(data["platform"], sensor)
# data = data.loc[valid]
data = data.drop(["platform", "std"], axis=1)
daily_dates = pd.to_datetime(pd.date_range(start_date, end_date, freq="D"))


site = []
ts_array = []
fig2, ax2 = plt.subplots()
for i in data["fid"].unique():
    fig, axs = plt.subplots(nrows=3, sharex=True)
    id = data["fid"] == i
    subset = data.loc[id]
    subset = subset.set_index("date")
    monthly_df = subset.resample("ME").mean()
    monthly_df = monthly_df["mean"].interpolate(method='time')

    daily_df = pd.DataFrame({"date": daily_dates})
    daily_df = daily_df.merge(subset, on="date", how="left")
    daily_df = daily_df.set_index("date")
    daily_df = daily_df["mean"].interpolate(method='time')
    site.append(i)
    dates = daily_df.index.to_pydatetime().tolist()
    ts = MSTL(daily_df,
              periods=365, windows=5 * 365, iterate=5,
              stl_kwargs=stl_kwargs).fit()
    axs[0].plot(ts.observed.index, ts.observed.values, label=i)
    axs[0].set_ylabel("observed values")
    axs[1].plot(ts.trend.index, ts.trend.values, label=i)
    axs[1].set_ylabel("trend")
    axs[2].plot(ts.seasonal.index, ts.seasonal.values, label=i)
    axs[2].set_ylabel("seasonal trend")


    ts = MSTL(monthly_df,
              periods=12, windows=5*12+1, iterate=5,
              stl_kwargs=stl_kwargs).fit()
    axs[0].plot(ts.observed.index, ts.observed.values, label=i)
    axs[0].set_ylabel("observed values")
    axs[1].plot(ts.trend.index, ts.trend.values, label=i)
    axs[1].set_ylabel("trend")
    axs[2].plot(ts.seasonal.index, ts.seasonal.values, label=i)
    axs[2].set_ylabel("seasonal trend")
    ts_array.append(ts)
    ax2.plot(ts.trend.index, ts.trend.values, label=i)


ax2.set_ylabel("seasonal trend")
ax2.legend()
plt.show()
