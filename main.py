import time as imported_time

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

start_time = imported_time.time()

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

name_state = "Kentucky"
# name_state = "United States Virgin Islands"
df = pd.read_csv(f"{name_state}.csv", header=None, names=[0, 1])
# Lấy dữ liệu từ cột A và chuyển nó thành list con (tối đa 250 phần tử mỗi list con)
list_lat = [df[0][i:i + 250].tolist() for i in range(0, len(df[0]), 250)]

# Lấy dữ liệu từ cột B và chuyển nó thành list con (tối đa 250 phần tử mỗi list con)
list_lon = [df[1][i:i + 250].tolist() for i in range(0, len(df[1]), 250)]
# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
for j in range(17, len(list_lat)):
    params = {
        "latitude": list_lat[j],
        "longitude": list_lon[j],
        "start_date": "2023-10-26",
        "end_date": "2023-11-09",
        "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "snow_depth"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # # Process first location. Add a for-loop for multiple locations or weather models
    # response = responses[1]
    i = 0
    for response in responses:
        print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
        # Số lượng thoi tiet mỗi tọa độ
        temperatures_per_coordinate = 24 * 15
        latitude_index = i // temperatures_per_coordinate
        longitude_index = i // temperatures_per_coordinate
        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_rain = hourly.Variables(2).ValuesAsNumpy()
        hourly_snow_depth = hourly.Variables(3).ValuesAsNumpy()
        hourly_data = {
            "date": pd.date_range(start=pd.to_datetime(hourly.Time(), unit="s"),
                                  end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                                  freq=pd.Timedelta(seconds=hourly.Interval()), inclusive="left")}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["rain"] = hourly_rain
        hourly_data["snow_depth"] = hourly_snow_depth
        hourly_data["lat"] = list_lat[0][i]
        hourly_data["lon"] = list_lon[0][i]
        hourly_dataframe = pd.DataFrame(data=hourly_data)

        csv_filename = f"{name_state}_weather_data_{j}.csv"
        hourly_dataframe.to_csv(csv_filename, mode='a', index=False, header=i == 0)
        print(f"DataFrame đã được lưu vào '{csv_filename}'.")
        i += 1
end_time = imported_time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy chương trình: {execution_time} giây")
