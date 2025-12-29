import hashlib
from db import db

class User:
    @staticmethod
    def hash_password(password):
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register(username, password):
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = db.execute_query("SELECT * FROM users WHERE username = %s", (username,))
        if existing_user:
            return False, "用户名已存在"
        
        # 对密码进行哈希处理
        hashed_password = User.hash_password(password)
        
        # 插入新用户
        result = db.execute_update(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        
        if result > 0:
            return True, "注册成功"
        else:
            return False, "注册失败"
    
    @staticmethod
    def login(username, password):
        """用户登录"""
        # 查找用户
        user = db.execute_query("SELECT * FROM users WHERE username = %s", (username,))
        if not user:
            return None, "用户名不存在"
        
        user = user[0]
        # 验证密码
        hashed_password = User.hash_password(password)
        if hashed_password == user['password']:
            return user, "登录成功"
        else:
            return None, "密码错误"
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户信息"""
        users = db.execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
        return users[0] if users else None