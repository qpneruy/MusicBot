# import pymysql
#
# # Thay thế các giá trị này bằng chi tiết máy chủ MySQL của bạn
# host = 'localhost'
# user = 'root'
# password = ''
# # database = 'discord_guild'a
#
# # Dữ liệu cần chèn
# new_data = {
#     'ten_server': 'new_server',
#     'voice_id': 'new_voice_id',
#     'gpt_channel_id': 'new_gpt_channel_id',
#     'bard_channel_id': 'new_bard_channel_id',
#     'vol_up': 1,
#     'vol_down': 2
# }
#
# # Kết nối tới cơ sở dữ liệu
# connection = pymysql.connect(host=host, user=user, password=password, database=database)
#
# try:
#     with connection.cursor() as cursor:
#         # Tạo bảng nếu chưa tồn tại
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS server_data (
#             id INT AUTO_INCREMENT NOT NULL,
#             ten_server VARCHAR(255) NOT NULL,
#             voice_id VARCHAR(255) NOT NULL,
#             gpt_channel_id VARCHAR(255) NOT NULL,
#             bard_channel_id VARCHAR(255) NOT NULL,
#             current_vol INT NOT NULL,
#             PRIMARY KEY (id)
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """
#         cursor.execute(create_table_query)
#
#         # Chèn dữ liệu mới
#         insert_data_query = """
#         INSERT INTO server_data (ten_server, voice_id, gpt_channel_id, bard_channel_id, current_vol)
#         VALUES (%(ten_server)s, %(voice_id)s, %(gpt_channel_id)s, %(bard_channel_id)s, %(current_vol)s)
#         """
#         cursor.execute(insert_data_query, data_to_insert)
#
#         # Truy vấn dữ liệu từ bảng
#         select_query = "SELECT * FROM server_data"
#         cursor.execute(select_query)
#         result = cursor.fetchall()
#
#         # In ra kết quả
#         for row in result:
#             print(row)
#
# finally:
#     # Xác nhận các thay đổi và đóng kết nối
#     connection.commit()
#     connection.close()


