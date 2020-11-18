import pymysql


class MySQL:
    def __init__(self, host, user, password, db, port=3306):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "無資料庫連線資訊")
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.db, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "資料庫連接失敗!")
        else:
            return cur

    def fetchAll(self, sql, args=None):
        cur = self.__GetConnect()
        if args is not None:
            args = tuple(map(str, args))
        cur.execute(sql, args)
        resList = cur.fetchall()

        self.conn.close()
        return resList

    def execute(self, sql, args=None):
        cur = self.__GetConnect()
        if args is not None:
            args = tuple(map(str, args))
        cur.execute(sql, args)
        self.conn.commit()
        self.conn.close()
