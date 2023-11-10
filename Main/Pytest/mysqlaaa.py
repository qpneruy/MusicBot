import mysql.connector

# Thay đổi thông tin kết nối theo cơ sở dữ liệu của bạn
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="NgHan71!",
    database="discord_db"
)
cursor = mydb.cursor()

# SQL truy vấn để chèn giá trị vào bảng
insert_query = "INSERT INTO data (name, age) VALUES (%s, %s)"
values = ("John Doe", 30)  # Thay đổi giá trị tùy theo dữ liệu bạn muốn chèn

# Thực thi truy vấn chèn giá trị
cursor.execute(insert_query, values)

# Lưu các thay đổi
connection.commit()

# Đóng kết nối
cursor.close()
connection.close()