import pymysql

cnx = pymysql.connect(host='localhost', user='root', password='', database='discord_guild')

cur = cnx.cursor()
#cur.execute('ALTER TABLE server_data ADD COLUMN last_channel VARCHAR(255)')
cur.execute('SELECT current_vol FROM server_data WHERE  = 0.5')
res = cur.fetchone()
print(res)
cnx.commit()