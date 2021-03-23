from dbms import DB

db = DB('site.db')

db.create_user_table()
db.create_sensor_table()
