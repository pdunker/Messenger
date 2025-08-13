from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pytz import utc, timezone

# local implementation:
db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "SECRET_KEY_COMES_HERE"

    # local implementation:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    # server implementation:
    """
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="",
        password="",
        hostname="",
        databasename="",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    global db
    db = SQLAlchemy(app)
    """
    # server implementation end

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, PrivateChat, PrivateMsg, Post
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Log in to access this page"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def get_date_str(date):
        br_date = date
        # server implementation:
        """
        utc_date = utc.localize(date)
        br_date = utc_date.astimezone(timezone("Brazil/East"))
        """
        return br_date.strftime("%Y-%m-%d %H:%M:%S")

    app.jinja_env.globals.update(get_date_str=get_date_str)

    def get_len(a_list):
        return len(a_list)

    app.jinja_env.globals.update(get_len=get_len)

    app.logger.debug(" ### create_app() done!")
    return app


