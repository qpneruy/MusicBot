import os
import requests
import json

# print("Nhập số điện thoại: ")
# phone_number = input(str())
# print("Chọn học kỳ: ")
# hocky = int(input())
phone_number = '0707147439'
hocky = 1
"""----Tìm mã học sinh----"""
data = requests.get(
    f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery1124005198661811961358_1700195389759&call=solienlac.search&search={phone_number}&tinh_id=7&_=1700195389760")
curr_data = data.text
curr_data = curr_data[curr_data.find("(") + 1: curr_data.find("])") + 1]
curr_data = json.loads(curr_data)
with open("data.json", "w") as f:
    json.dump(curr_data, f, indent=4)
ma = curr_data[0]["ma_hoc_sinh"]
data = requests.get("https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery112407080939953947958_1700287590972&call=solienlac.getDSNamhoc&mahocsinh=2107435057&tinh_id=7&_=1700287590973")
"""----Gửi yêu cấu Lấy Xác nhận Kết nối----"""
data = requests.get(
    f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757&call=solienlac.checkSll&mahocsinh={ma}&tinh_id=7&password={phone_number}&namhoc=2023&dot_diem_id=0&_=1700195483760")
cookies = data.cookies
"""----Lấy dữ liệu bảng điểm----"""
data = requests.get(
    f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757&call=solienlac.getSodiem&mahocsinh={ma}&key=d33e425220d1f1184a9fb9a477055fd6&namhoc=2023&tinh_id=7&dot_diem_id=0&_=1700195483761",
    cookies=cookies)
curr_data = data.text
curr_data = curr_data[curr_data.find("({") + 1: curr_data.find("})") + 1]
curr_data = json.loads(curr_data)
with open("data_2.json", "w") as f:
    json.dump(curr_data, f, indent=4)
hocky = hocky - 1
for items in curr_data["diem"][hocky]["mon_hoc"]:
    print()
    print(items["ten_mon_hoc"], end=' ')
    for itemss in items["TX"]:
        print(itemss["diem"], end=' ')
    if items["GK"]:
        print(f"> GK: {items['GK'][0]['diem']}", end=' ')
    else:
        print(f"> GK: Chưa nhập", end=' ')
