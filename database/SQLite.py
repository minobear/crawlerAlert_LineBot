import sqlite3


class SQLite:
    def __init__(self, filename):
        self.filename = filename
        self.conn = self.__get_connection()
        self.cur = self.conn.cursor()

    def __get_connection(self):
        return sqlite3.connect(self.filename)

    def fetchAll(self, sql, args=None):
        if args:
            args = tuple(map(str, args))
            self.cur.execute(sql, args)
        else:
            self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def execute(self, sql, args=None):
        if args:
            args = tuple(map(str, args))
            self.cur.execute(sql, args)
        else:
            self.cur.execute(sql)
        self.conn.commit()