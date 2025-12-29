from flask import Flask, request, jsonify
from flask_cors import CORS
import auth
import voting
import init_db

# 初始化Flask应用
app = Flask(__name__)
# 允许所有跨域请求（开发环境简化配置，生产环境可限定域名）
CORS(app)

# 全局初始化数据库表（启动后端时自动执行）
init_db.DatabaseInitializer.create_tables()

# -------------------------- 接口定义 --------------------------
@app.route('/api/register', methods=['POST'])
def api_register():
    """用户注册接口"""
    try:
        # 获取前端提交的JSON数据
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 参数验证
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '请输入用户名和密码'
            }), 400

        # 调用原有注册逻辑
        success, message = auth.User.register(username, password)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册异常：{str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """用户登录接口"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '请输入用户名和密码'
            }), 400

        # 调用原有登录逻辑
        user, message = auth.User.login(username, password)
        return jsonify({
            'success': True if user else False,
            'message': message,
            'data': user  # 登录成功返回用户信息，失败返回null
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录异常：{str(e)}'
        }), 500

@app.route('/api/polls', methods=['GET'])
def api_get_all_polls():
    """获取所有投票接口"""
    try:
        polls = voting.Poll.get_all_polls()
        return jsonify({
            'success': True,
            'data': polls
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取投票列表异常：{str(e)}'
        }), 500

@app.route('/api/polls', methods=['POST'])
def api_create_poll():
    """创建投票接口"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        creator_id = data.get('creator_id')
        options = data.get('options', [])

        # 参数验证
        if not title:
            return jsonify({
                'success': False,
                'message': '请输入投票主题'
            }), 400
        if len(options) < 2:
            return jsonify({
                'success': False,
                'message': '至少需要两个有效的投票选项'
            }), 400

        # 调用原有创建投票逻辑
        success, poll_id, message = voting.Poll.create_poll(title, description, creator_id, options)
        return jsonify({
            'success': success,
            'message': message,
            'data': {'poll_id': poll_id}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建投票异常：{str(e)}'
        }), 500

@app.route('/api/polls/<int:poll_id>', methods=['GET'])
def api_get_poll_detail(poll_id):
    """获取单个投票详情接口"""
    try:
        poll = voting.Poll.get_poll_by_id(poll_id)
        if not poll:
            return jsonify({
                'success': False,
                'message': '投票不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': poll
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取投票详情异常：{str(e)}'
        }), 500

@app.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
def api_submit_vote(poll_id):
    """提交投票接口"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        option_id = data.get('option_id')

        # 调用原有投票逻辑
        success, message = voting.Poll.vote(user_id, poll_id, option_id)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'提交投票异常：{str(e)}'
        }), 500

@app.route('/api/user/polls', methods=['GET'])
def api_get_user_created_polls():
    """获取当前用户创建的投票接口"""
    try:
        # 从请求参数中获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID'
            }), 400

        polls = voting.Poll.get_user_created_polls(int(user_id))
        return jsonify({
            'success': True,
            'data': polls
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取我的投票异常：{str(e)}'
        }), 500

# -------------------------- 启动后端 --------------------------
if __name__ == '__main__':
    # Windows环境下启动Flask，端口5000，允许外部访问，关闭调试模式（生产环境推荐）
    app.run(host='0.0.0.0', port=5000, debug=False)