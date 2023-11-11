import pandas as pd
# Đọc dữ liệu từ tệp CSV vào một DataFrame
name_state = "Kentucky"
# name_state = "United States Virgin Islands"
df = pd.read_csv(f"{name_state}.csv", header=None, names=[0, 1])
# Lấy dữ liệu từ cột A và chuyển nó thành list con (tối đa 250 phần tử mỗi list con)
list_lat = [df[0][i:i + 250].tolist() for i in range(0, len(df[0]), 250)]

# Lấy dữ liệu từ cột B và chuyển nó thành list con (tối đa 250 phần tử mỗi list con)
list_lon = [df[1][i:i + 100].tolist() for i in range(0, len(df[1]), 100)]
print(len(list_lat))
print(len(list_lon))
# print(list_lon)