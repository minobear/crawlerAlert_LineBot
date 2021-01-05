"""
Using MySQL
"""
# import socket
#
# from database.MySQL import MySQL
#
# pc_name = socket.gethostname()
# ip = "103.136.210.188" if pc_name == "MINO-PC" else "127.0.0.1"
# db = MySQL(ip, "line_bot", "5d8976c042", "line_bot")
from database.SQLite import SQLite

"""
    Using SQLite
"""
db = SQLite("./record.sqlite")