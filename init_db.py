from db import db

class DatabaseInitializer:
    @staticmethod
    def create_tables():
        """创建数据库表结构"""
        # 创建用户表
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.execute_update(users_table_sql)
        print("用户表创建成功")
        
        # 创建投票表
        polls_table_sql = """
        CREATE TABLE IF NOT EXISTS polls (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            creator_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
        """
        db.execute_update(polls_table_sql)
        print("投票表创建成功")
        
        # 创建选项表
        options_table_sql = """
        CREATE TABLE IF NOT EXISTS options (
            id INT AUTO_INCREMENT PRIMARY KEY,
            poll_id INT NOT NULL,
            option_text VARCHAR(255) NOT NULL,
            FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE
        )
        """
        db.execute_update(options_table_sql)
        print("选项表创建成功")
        
        # 创建投票记录表
        votes_table_sql = """
        CREATE TABLE IF NOT EXISTS votes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            poll_id INT NOT NULL,
            option_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE,
            FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_poll (user_id, poll_id)  # 确保用户对每个投票只能投一次
        )
        """
        db.execute_update(votes_table_sql)
        print("投票记录表创建成功")

if __name__ == "__main__":
    # 初始化数据库表
    DatabaseInitializer.create_tables()
    print("所有数据库表创建完成")