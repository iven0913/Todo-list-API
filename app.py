from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, LoginManager, current_user, login_user, UserMixin

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypassword@127.0.0.1:13306/todolist_demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def get_id(self):
        return self.id


class TodoItem(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item = db.Column(db.String(55), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    date = db.Column(db.DATETIME, default=datetime.now)


# with app.app_context():
#     db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(id_):
    return User.query.filter_by(id=id_).first()


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 驗證使用者
        # 寫法1 用filter
        # db.session.query(User).filter(User.username == username).first()
        # 寫法2 用filter_by
        # user1 = db.session.query(User).filter_by(username=username).first()
        # 寫法3
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # 認證使用者並記住登入狀態
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))

    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    username = current_user.username
    todo_list = TodoItem.query.all()
    return render_template('dashboard.html', username=username, todo_list=todo_list)


@app.route('/logout')
def logout():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    item = request.form['item']  # 從 request 取得輸入的 item value
    date = request.form['date']  # 從 request 取得輸入的 time value
    # Add new record to table 'TodoItem'
    db.session.add(
        TodoItem(item=item, date=date)
    )
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.get('/update/<int:item_id>')
def render_update(item_id):
    if not (todo := TodoItem.query.filter_by(id=item_id).first()):
        return redirect(url_for('dashboard'))
    return render_template("edit.html", todo=todo)


@app.post('/update/<int:item_id>')
def update(item_id):
    if (todo := TodoItem.query.filter_by(id=item_id).first()) is not None:
        todo.item = request.form["todo"]
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/check/<int:item_id>')
def check(item_id):
    """
    打勾 or 取消 TodoItem 的完成狀態
    1. 如果找不到 TodoItem 的話： 就回到 dashboard
    2. 如果找到了且 TodoItem 是完成的：那就把 TodoItem 的 is_done 變成 False，就回到 dashboard
    3. 如果找到了且 TodoItem 是未完成的： 那就把 TodoItem 的 is_done 變成 True，就回到 dashboard
    """
    # := 象牙符號，在 python 代表在 if 裡面的 assign ( todo = TodoItem.query.filter_by(id=item_id).first())
    # 記住：只有 Python 可以這樣寫
    if todo := TodoItem.query.filter_by(id=item_id).first():
        # 縮減版本（記住：只有 Python 可以這樣寫）：todo.is_done = True if todo.is_done is False else False
        # 找到TodoItem
        if todo.is_done:
            # TodoItem 是完成的
            todo.is_done = False
        else:
            # TodoItem 不是完成的
            todo.is_done = True
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:item_id>')
def delete(item_id):
    todo = TodoItem.query.get(item_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
