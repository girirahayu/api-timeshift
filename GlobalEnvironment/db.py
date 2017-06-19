# import pymysql
import pymysql.cursors

# Connect to the database

class DB(object):
    conn = None
    def connect(self):
        self.conn = pymysql.connect(host='10.3.3.96',
                                     user='root',
                                     password='qwerty',
                                     db='timeshift',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def query(self,type,query,params):
        try:
            self.connect()
            self.cur = self.conn.cursor()
            if type == "insert" or type == "update":
                self.cur.execute(query,params)
                self.conn.commit()
            if type == "select":
                if params is None:
                    self.cur.execute(query)
                else:
                    self.cur.execute(query,params)
                result = self.cur.fetchall()
                return result
        except (AttributeError, pymysql.OperationalError):
            self.connect()
            self.cur = self.conn.cursor()
            if type == "insert" or type == "update":
                self.cur.execute(query,params)
                self.conn.commit()
            if type == "select":
                if params is None:
                    self.cur.execute(query)
                else:
                    self.cur.execute(query,params)
                result = self.cur.fetchall()
                return result
        except pymysql.MySQLError as e:
            error = ('Got error {!r}, errno is {}'.format(e, e.args[0]))
            print error

    def curclose(self):
        return self.cur.close()
    def close(self):
        return self.conn.close()

