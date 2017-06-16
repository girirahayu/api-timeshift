# import pymysql
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='10.3.3.96',
                             user='root',
                             password='qwerty',
                             db='timeshift',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

class DB(object):
    def query(self,type,query,params):
        try:
            if type == "insert" or type == "update":
                with connection.cursor() as cursor:
                    cursor.execute(query,params)
                connection.commit()
            if type == "select":
                if params is None:
                    with connection.cursor() as cursor:
                        cursor.execute(query)
                else:
                    with connection.cursor() as cursor:
                        cursor.execute(query,params)
                result = cursor.fetchall()
                return result
        except (AttributeError, pymysql.OperationalError):
            if type == "insert" or type == "update":
                with connection.cursor() as cursor:
                    cursor.execute(query,params)
                connection.commit()
            if type == "select":
                if params is None:
                    with connection.cursor() as cursor:
                        cursor.execute(query)
                else:
                    with connection.cursor() as cursor:
                        cursor.execute(query,params)
                result = cursor.fetchall()
                return result

        except pymysql.MySQLError as e:
            error = ('Got error {!r}, errno is {}'.format(e, e.args[0]))
            print error

    def close(self):
        return connection.close()
