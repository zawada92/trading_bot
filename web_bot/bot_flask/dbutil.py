import click
import datetime

from flask import g
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
db.contract_list = ["BTC_USDT", "ETH_USDT"]


class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    notification = db.relationship("Notification", backref="user", lazy=True)


class Notification(db.Model):
    """Notification model."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    issued = db.Column(db.DateTime)
    contract_name = db.Column(
        db.String(15), db.ForeignKey("contract.contract_name"), nullable=False
    )
    request_price = db.Column(db.Numeric, nullable=False)
    trend = db.Column(db.Integer, nullable=False)


class Contract(db.Model):
    """Contract model."""

    contract_name = db.Column(db.String(15), unique=True, primary_key=True)
    current_price = db.Column(db.Numeric)
    latest_price = db.Column(db.Numeric)
    notification = db.relationship(
        "Notification", backref="contract", lazy=True
    )
    ohlc = db.relationship("OhlcCandle", backref="contract", lazy=True)


class OhlcCandle(db.Model):
    """OhlcCandle model."""

    id = db.Column(db.Integer, primary_key=True)
    contract_name = db.Column(
        db.String(15), db.ForeignKey("contract.contract_name")
    )
    candle_id = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    open = db.Column(db.Numeric)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    close = db.Column(db.Numeric)


def get_db():
    """Binds database to g global object if not present.

    Returns:
        SQLAlchemy: Database instance
    """
    if "db" not in g:
        g.db = db

    return g.db


def init_db_tables():
    """Clear existing data and create tables with required initial content."""
    db = get_db()
    db.drop_all()
    db.create_all()

    for contract_str in db.contract_list:
        contract = Contract(contract_name=contract_str)
        db.session.add(contract)

        create_20_initial_candles(db, contract_str)
    db.session.commit()


def create_20_initial_candles(db: SQLAlchemy, contract_str: str) -> None:
    """Creates 20 initial candles with zeroed values.

    Params:
        db(SQLAlchemy): Database
        contract_str(str): Contract name
    """
    for index in range(0, 20):
        candle = OhlcCandle(
            contract_name=contract_str,
            candle_id=index,
            time=datetime.datetime.now(),
            open=0,
            high=0,
            low=0,
            close=0,
        )
        db.session.add(candle)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Command line function to initialize database."""
    init_db_tables()
    click.echo("Initialized the database.")


def close_db(e=None):
    """Closes db on app teardown."""
    g.pop("db", None)


def init_app_db(app):
    """Bind app with db. Sets init-db command and close db on app teardown.

    Params:
        app(Flask): Flask app instance
    """
    db.app = app
    db.init_app(app)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
