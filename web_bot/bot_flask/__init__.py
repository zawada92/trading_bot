import logging
import os

from flask import Flask
from flask_apscheduler import APScheduler
from werkzeug.debug import DebuggedApplication

from bot_flask.dbutil import db
from bot_flask.notification_util import job_fetch_and_notify


def job_fetch_and_notify_1m() -> None:
    """Job executed every 1 minute. Fetches actual data from
    exchange and sends notification.
    """
    with db.app.app_context():
        job_fetch_and_notify()


class Config:
    """Configuration class for Flask app settings."""

    JOBS = [
        {
            "id": "job_1m",
            "func": "bot_flask:job_fetch_and_notify_1m",
            "args": (),
            "trigger": "interval",
            "seconds": 60,
        },
    ]
    SECRET_KEY = "dev"
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    DEBUG = True


def create_app() -> Flask:
    """Creates Flask app instance using Config object settings.
    Registers blueprints and initializes scheduler. Used as app factory
    in gunicorn command.

    Returns:
        Flask: instance of Flask app.
    """
    app = Flask(__name__)

    app.config.from_object(Config())
    app.logger.setLevel(logging.INFO)
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
    app.app_context().push()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from bot_flask import dbutil

    dbutil.init_app_db(app)

    from bot_flask import auth

    app.register_blueprint(auth.auth_bp)

    from bot_flask import auto_trader

    app.register_blueprint(auto_trader.auto_trader_bp)

    from bot_flask import notification_util

    app.register_blueprint(notification_util.notification_bp)

    app.add_url_rule("/", endpoint="index")
    app.add_url_rule("/auth", endpoint="auth")
    app.add_url_rule("/notifications", endpoint="notifications.index")

    # initialize scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    return app


if __name__ == "__main__":
    # Used when debugging in VSCode
    app = create_app()
    # To use VSCode debugging need to disable flask debug
    app.run(port=5000, debug=False)
