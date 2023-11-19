import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Vnedu:
    def __init__(self):
        self.hocky = 0
        self.curr_data = None

    def _get_diem(self, sdt: str, password: str) -> any:
        phone_number = sdt
        self.hocky = 1
        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery1124005198661811961358_1700195389759&call=solienlac.search&search={phone_number}&tinh_id=7&_=1700195389760")
        curr_data = json.loads(data.text[data.text.find("(") + 1: data.text.find("])") + 1])
        # with open("../Main/data.json", "w") as f:
        #     json.dump(curr_data, f, indent=4)

        ma = curr_data[0]["ma_hoc_sinh"]

        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery112407080939953947958_1700287590972&call=solienlac.getDSNamhoc&mahocsinh={ma}&tinh_id=7&_=1700287590973")

        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757&call=solienlac.checkSll&mahocsinh={ma}&tinh_id=7&password={password}&namhoc=2023&dot_diem_id=0&_=1700195483760")

        cookies = data.cookies

        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757&call=solienlac.getSodiem&mahocsinh={ma}&key=d33e425220d1f1184a9fb9a477055fd6&namhoc=2023&tinh_id=7&dot_diem_id=0&_=1700195483761",
            cookies=cookies)
        curr_data = json.loads(data.text[data.text.find("({") + 1: data.text.find("})") + 1])
        # with open("../Main/data_2.json", "w") as f:
        #     json.dump(curr_data, f, indent=4)
        return curr_data

    def get_bang_diem(self, sdt: str, password: str) -> any:
        curr_data = self._get_diem(sdt, password)
        image = Image.open("D:\\Project\\Python\\qpneruy-Git\\modules\\bangdiem.png")
        draw = ImageDraw.Draw(image)
        pos_giua_ki = 600
        pos_cuoi_ki = 760
        pos_trung_binh = 835
        space_lift = 35
        font = ImageFont.truetype("D:\\Project\\Python\\qpneruy-Git\\modules\\Num_font1.ttf", 16)
        y_position = 45

        for items in curr_data["diem"][self.hocky-1]["mon_hoc"]:
            list_diem = []
            Sum = 0
            has_ck = False  # Kiểm tra xem có điểm cuối kỳ không
            if items["ten_mon_hoc"] in ["Âm nhạc", "Mĩ thuật", "Thể dục"]:
                continue
            for itemss in items["TX"]:
                list_diem.append(itemss["diem"])
                Sum += float(itemss["diem"])
            if items.get("GK") and items.get("GK") != "Đ":
                has_ck = True
                if len(list_diem) > 0:
                    draw.text((pos_trung_binh, y_position),
                              f"{round(((Sum + (float(items['GK'][0]['diem']) * 2)) / (len(list_diem) + 2)), 1)}",
                              font=font,
                              fill=(0, 0, 0))
            else:
                if len(list_diem) > 0:
                    draw.text((pos_trung_binh, y_position), f"{Sum / len(list_diem)}", font=font, fill=(0, 0, 0))
                else:
                    draw.text((pos_trung_binh, y_position), "Chưa Nhập", font=font, fill=(0, 0, 0))

            for i, diem in enumerate(list_diem, start=1):
                math_column_x = 150 + i * 29
                draw.text((math_column_x, y_position), str(diem), font=font, fill=(0, 0, 0))

            if items.get("GK"):
                draw.text((pos_giua_ki, y_position), f"{items['GK'][0]['diem']}", font=font, fill=(0, 0, 0))
            else:
                draw.text((pos_giua_ki, y_position), 'Chưa Nhập', font=font, fill=(0, 0, 0))

            if has_ck:
                ck = items.get("CK", [])
                if ck:
                    draw.text((pos_cuoi_ki, y_position), f"{ck[0]['diem']}", font=font, fill=(0, 0, 0))
                    ck_score = float(ck[0]['diem'])
                    total_score = (Sum + (ck_score * 2)) / (len(list_diem) + 3)  # Cộng thêm điểm cuối kỳ
                    draw.text((pos_trung_binh + 80, y_position),
                              f"{round(total_score, 1)}", font=font, fill=(0, 0, 0))

            y_position += space_lift

        img_io = BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io.getvalue()
