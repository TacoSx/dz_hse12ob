#Для авторизации
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskhse.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
#Регистрация
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Поле имя пользователя пустое.'
        elif not password:
            error = 'Поле пароля пустое'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Пользователь {username} уже зарегистрирован."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
#Авторизация
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Неправильное имя пользователя или пароль.'
        elif not check_password_hash(user['password'], password):
            error = 'Неправильное имя пользователя или пароль.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
#Работа с сессиями
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
#Выход пользователя
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#Проверка входа пользователя для создания изменени удалене доски
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view