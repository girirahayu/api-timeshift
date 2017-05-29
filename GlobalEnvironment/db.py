import pymysql.cursors

# # Connect to the database
class DB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = pymysql.connect(host='10.3.3.96',
                                 user='root',
                                 password='qwerty',
                                 db='timeshift',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        self._db_cur = self._db_connection.cursor()

    def close_cur(self):
        return self._db_connection.cursor().close

    def close_conn(self):
        return self._db_connection.close()

    def select(self, query, params):
        if not params:
            self._db_cur.execute(query)
        else:
            self._db_cur.execute(query,params)

        return self._db_cur.fetchall()

    def query(self,type,query,params):
        if type == "select":
            if params == 0:
                self._db_cur.execute(query)
            else:
                self._db_cur.execute(query, params)
            return self._db_cur.fetchall()

        if type == "insert" or type == "update":
            self._db_cur.execute(query,params)
            return self._db_connection.commit()
