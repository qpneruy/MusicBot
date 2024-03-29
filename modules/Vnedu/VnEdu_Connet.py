import json
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont


class VnEduConnect:
    student_id = ''
    period = 0
    phone_number = ''
    year = ''

    @classmethod
    def _get_ds_nam_hoc(cls):
        """Lấy danh sách năm học qua mã học sinh"""
        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery112409872379009080097_1700400232757"
            f"&call=solienlac.getDSNamhoc&mahocsinh={cls.student_id}&tinh_id=7&_=1700400232758")
        data_namhoc = json.loads(data.text[data.text.find("(") + 1: data.text.find("])") + 1])
        return data_namhoc

    @classmethod
    def _get_student(cls) -> any:
        """Lấy thông tin học sinh"""
        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery1124005198661811961358_1700195389759"
            f"&call=solienlac.search&search={cls.phone_number}&tinh_id=7&_=1700195389760")
        data_hocsinh = json.loads(data.text[data.text.find("(") + 1: data.text.find("])") + 1])
        if not data_hocsinh:
            return
        return data_hocsinh

    @classmethod
    def get_diem(cls, phone_number: str, password: str, period: int, year: str) -> any:
        """Lấy bảng điểm"""
        """---------------------------------------------------------"""
        # Lấy các giá trị khởi tạo cho hàm
        cls.year = year
        cls.period = period
        cls.phone_number = phone_number
        data_hocsinh = cls._get_student()
        """---------------------------------------------------------"""
        # Kiểm tra tính hợp lẹ của dữ liệu
        if not data_hocsinh:
            return ["Code1"]
        data_hoc_sinh_year = int(data_hocsinh[0]["nam_hoc"])
        provided_year = int(cls.year)
        if data_hoc_sinh_year < provided_year:
            return ["Code2", f"Không tồn tại khóa học năm {year}"]
        cls.student_id = data_hocsinh[0]["ma_hoc_sinh"]
        """-------------------------------------------------------"""
        # Lấy quyền truy cập sổ điểm
        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757"
            f"&call=solienlac.checkSll&mahocsinh={cls.student_id}&tinh_id=7&password={password}&namhoc="
            f"{year}&dot_diem_id=0&_=1700195483760")
        flags = json.loads(data.text[data.text.find("({") + 1: data.text.find("})") + 1])
        if not flags["success"]:
            return ["Code2", flags["msg"]]
        cookies = data.cookies
        """-------------------------------------------------------"""
        # Lấy dữ liệu bảng điểm
        data = requests.get(
            f"https://hocbadientu.vnedu.vn/sllservices/index.php?callback=jQuery11240405892063703583_1700195483757"
            f"&call=solienlac.getSodiem&mahocsinh={cls.student_id}&key=d33e425220d1f1184a9fb9a477055fd6&namhoc="
            f"{year}&tinh_id=7&dot_diem_id=0&_=1700195483761",
            cookies=cookies)
        score_data = json.loads(data.text[data.text.find("({") + 1: data.text.find("})") + 1])
        """-------------------------------------------------------"""
        # Tạo ảnh trả vè kết quả
        return cls._get_bang_diem(score_data)

    @classmethod
    def _get_bang_diem(cls, score_data: json) -> any:
        image = Image.open("D:\\Project\\Python\\qpneruy-Git\\modules\\Vnedu\\bangdiem.png")
        font = ImageFont.truetype("D:\\Project\\Python\\qpneruy-Git\\modules\\Vnedu\\Arial.ttf", 16)
        draw = ImageDraw.Draw(image)
        mid_period_pos = 600
        last_period_pos = 760
        avg_period_pos = 835
        space_lift = 35
        pos_y = 45
        total_avg = 0.0
        for items in score_data["diem"][cls.period - 1]["mon_hoc"]:
            dived = 0
            avg_subject = 0.0
            list_score = []
            if items["ten_mon_hoc"] in ["Âm nhạc", "Mĩ thuật", "Thể dục"]:
                continue
            """---------------------------------------------------------"""
            # Lấy và ghi cột điểm thường xuyên
            for score_colunm in items["TX"]:
                list_score.append(score_colunm["diem"])
                dived += 1
                avg_subject += float(score_colunm["diem"])
            """---------------------------------------------------------"""
            # Ghi điểm TX vào bảng
            for i, score in enumerate(list_score, start=1):
                score_postion_x = 150 + i * 29
                draw.text((score_postion_x, pos_y), str(score), font=font, fill=(0, 0, 0))
            """---------------------------------------------------------"""
            # Ghi điểm giữa cuối kì vào bảng
            if items.get("GK"):
                draw.text((mid_period_pos, pos_y), f"{items['GK'][0]['diem']}", font=font, fill=(0, 0, 0))
                dived += 2
                avg_subject += float(items['GK'][0]['diem']) * 2
            if items.get("CK"):
                draw.text((last_period_pos, pos_y), f"{items['CK'][0]['diem']}", font=font, fill=(0, 0, 0))
                dived += 3
                avg_subject += float(items['CK'][0]['diem']) * 3
            """---------------------------------------------------------"""
            # Xử lý dữ liệu
            reslut = round(avg_subject / dived, 1)
            total_avg += reslut
            draw.text((avg_period_pos, pos_y), str(reslut), font=font, fill=(0, 0, 0))
            pos_y += space_lift
        """--------------------------------------------------------------------------------"""
        draw.text((150, 525), str(round(total_avg / 11, 1)), font=font, fill=(0, 0, 0))
        student_detail = cls._get_student()
        ds_namhoc = cls._get_ds_nam_hoc()
        ten_lop = ""
        for items in ds_namhoc:
            if items["nam_hoc"] == cls.year:
                ten_lop = items["ten_lop"]
        """-----------------------------------------------------------------------------------"""
        # Ghi thêm thông tin
        draw.text((180, 425), str(student_detail[0]["full_name"]), font=font, fill=(0, 0, 0))
        draw.text((530, 425), ten_lop, font=font, fill=(0, 0, 0))
        draw.text((600, 425), str(student_detail[0]["ten_truong"]), font=font, fill=(0, 0, 0))
        draw.text((145, 595), str(score_data["diem"][cls.period - 1]["tong_ket"]["hoc_luc"]), font=font, fill=(0, 0, 0))
        draw.text((145, 625), str(score_data["diem"][cls.period - 1]["tong_ket"]["hanh_kiem"]), font=font,
                  fill=(0, 0, 0))
        draw.text((145, 560), str(score_data["diem"][cls.period - 1]["hang"]), font=font, fill=(0, 0, 0))
        draw.text((555, 530), str(score_data["diemdanh"][0]), font=font, fill=(0, 0, 0))
        draw.text((555, 578), str(score_data["diemdanh"][1]), font=font, fill=(0, 0, 0))
        draw.text((555, 625), str(score_data["diemdanh"][2]), font=font, fill=(0, 0, 0))
        """-----------------------------------------------------------------------------------"""
        img_io = BytesIO()
        image.save('diem.png')
        image.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io.getvalue()
