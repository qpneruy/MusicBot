from easy_pil import aio_editor
import PIL
from PIL import Image, ImageDraw, ImageFont


def add_math_column(image_path, output_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    pos_giua_ki = 600
    pos_cuoi_ki = 760
    pos_trung_binh = 835
    space_lift = 40
    font = ImageFont.truetype("Num_font1.ttf", 16)
    diem_toan = [10, 9, 8, 10, 7]
    y_position = 44
    math_column_x = 150
    for i, diem in enumerate(diem_toan):
        math_column_x += 29
        draw.text((math_column_x, y_position), str(diem), font=font, fill=(0, 0, 0))
    draw.text((pos_giua_ki, 43), '10', font=font, fill=(0, 0, 0))
    draw.text((pos_cuoi_ki, 43), '10', font=font, fill=(0, 0, 0))
    draw.text((pos_trung_binh, 43), '10', font=font, fill=(0, 0, 0))
    math_column_x = 150
    for i, diem in enumerate(diem_toan):
        math_column_x += 29
        draw.text((math_column_x, y_position+space_lift), str(diem), font=font, fill=(0, 0, 0))
    image.save(output_path)


# Đường dẫn của hình ảnh ban đầu và hình ảnh sau khi thêm cột điểm môn Toán
input_image_path = "../modules/bangdiem.png"
output_image_path = "a.png"

# Gọi hàm để thêm cột điểm môn Toán
add_math_column(input_image_path, output_image_path)
