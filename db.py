import pymysql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            # 如果数据库不存在，尝试创建数据库
            try:
                temp_conn = pymysql.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    charset='utf8mb4'
                )
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
                temp_cursor.close()
                temp_conn.close()
                print(f"数据库 {DB_NAME} 创建成功")
                # 重新连接到新创建的数据库
                self.connect()
            except Exception as e:
                print(f"创建数据库失败: {e}")
    
    def execute_query(self, query, params=None):
        """执行SQL查询"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """执行SQL更新（插入、更新、删除）"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(f"更新执行失败: {e}")
            self.connection.rollback()
            return 0
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# 创建全局数据库实例
db = Database()