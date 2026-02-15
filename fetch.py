import sqlite3

conn = sqlite3.connect("train.db")
cur = conn.cursor()

cur.execute("""
        SELECT * FROM TRAIN
        """)

res = cur.fetchall()
for i in res:
    print(i)