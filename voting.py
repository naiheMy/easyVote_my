from db import db

class Poll:
    @staticmethod
    def create_poll(title, description, creator_id, options):
        """创建投票"""
        try:
            # 开启事务
            if not db.connection or not db.connection.open:
                db.connect()
            
            # 插入投票信息
            db.execute_update(
                "INSERT INTO polls (title, description, creator_id) VALUES (%s, %s, %s)",
                (title, description, creator_id)
            )
            poll_id = db.cursor.lastrowid
            
            # 插入投票选项
            for option_text in options:
                db.execute_update(
                    "INSERT INTO options (poll_id, option_text) VALUES (%s, %s)",
                    (poll_id, option_text)
                )
            
            db.connection.commit()
            return True, poll_id, "投票创建成功"
        except Exception as e:
            if db.connection:
                db.connection.rollback()
            print(f"创建投票失败: {e}")
            return False, None, "投票创建失败"
    
    @staticmethod
    def get_all_polls():
        """获取所有投票"""
        polls = db.execute_query(
            "SELECT p.*, u.username as creator_name FROM polls p JOIN users u ON p.creator_id = u.id ORDER BY p.created_at DESC"
        )
        return polls
    
    @staticmethod
    def get_poll_by_id(poll_id):
        """根据ID获取投票详情"""
        # 获取投票基本信息
        polls = db.execute_query(
            "SELECT p.*, u.username as creator_name FROM polls p JOIN users u ON p.creator_id = u.id WHERE p.id = %s",
            (poll_id,)
        )
        
        if not polls:
            return None
        
        poll = polls[0]
        
        # 获取投票选项
        options = db.execute_query(
            "SELECT * FROM options WHERE poll_id = %s",
            (poll_id,)
        )
        poll['options'] = options
        
        # 获取每个选项的投票数
        for option in options:
            votes = db.execute_query(
                "SELECT COUNT(*) as vote_count FROM votes WHERE option_id = %s",
                (option['id'],)
            )
            option['vote_count'] = votes[0]['vote_count'] if votes else 0
        
        # 计算总投票数
        total_votes = sum(option['vote_count'] for option in options)
        poll['total_votes'] = total_votes
        
        return poll
    
    @staticmethod
    def user_has_voted(user_id, poll_id):
        """检查用户是否已经投过票"""
        votes = db.execute_query(
            "SELECT * FROM votes WHERE user_id = %s AND poll_id = %s",
            (user_id, poll_id)
        )
        return len(votes) > 0
    
    @staticmethod
    def vote(user_id, poll_id, option_id):
        """用户投票"""
        # 检查是否已经投过票
        if Poll.user_has_voted(user_id, poll_id):
            return False, "您已经投过票了"
        
        # 检查选项是否属于该投票
        options = db.execute_query(
            "SELECT * FROM options WHERE id = %s AND poll_id = %s",
            (option_id, poll_id)
        )
        if not options:
            return False, "无效的投票选项"
        
        # 执行投票
        result = db.execute_update(
            "INSERT INTO votes (user_id, poll_id, option_id) VALUES (%s, %s, %s)",
            (user_id, poll_id, option_id)
        )
        
        if result > 0:
            return True, "投票成功"
        else:
            return False, "投票失败"
    
    @staticmethod
    def get_user_votes(user_id):
        """获取用户参与的投票"""
        votes = db.execute_query(
            "SELECT p.*, o.option_text as voted_option, v.created_at as vote_time "
            "FROM votes v JOIN polls p ON v.poll_id = p.id "
            "JOIN options o ON v.option_id = o.id "
            "WHERE v.user_id = %s ORDER BY v.created_at DESC",
            (user_id,)
        )
        return votes
    
    @staticmethod
    def get_user_created_polls(user_id):
        """获取用户创建的投票"""
        polls = db.execute_query(
            "SELECT * FROM polls WHERE creator_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        return polls