import os
from flask import Flask

def create_app(test_config=None):
    # Базовая конфигурация
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='HSEDev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Загрузка конфига
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #иницилизируем бд
    from . import db
    db.init_app(app)
    #Блупринт авторизации
    from . import auth
    app.register_blueprint(auth.bp)
    #Блупринт поста
    from . import post
    app.register_blueprint(post.bp)
    app.add_url_rule('/', endpoint='index')




    return app