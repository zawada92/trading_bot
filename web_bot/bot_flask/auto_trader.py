import plotly.graph_objects as go

from flask import Blueprint, render_template, request
from pandas import read_sql

from bot_flask.dbutil import OhlcCandle, get_db


auto_trader_bp = Blueprint("auto_trader", __name__)


@auto_trader_bp.route("/")
def index():
    # TODO docstrings in routes
    return render_template("auto_trader/index.html")


@auto_trader_bp.route("/charts", methods=["GET"])
def charts():
    args = request.args
    contract_str = args.get("contract")
    if contract_str == None:
        contract_str = "BTC_USDT"

    db = get_db()
    df = read_sql(
        OhlcCandle.query.filter_by(contract_name=contract_str)
        .order_by(OhlcCandle.candle_id)
        .statement,
        db.session.connection(),
    )
    trace = go.Candlestick(
        x=df["time"].tolist(),
        open=df["open"].tolist(),
        high=df["high"].tolist(),
        low=df["low"].tolist(),
        close=df["close"].tolist(),
        name="name",
    )
    data = [trace]

    layout = {"title": contract_str, "xaxis_rangeslider_visible": False}

    fig = dict(data=data, layout=layout)

    return render_template(
        "auto_trader/charts.html", df=go.Figure(fig).to_dict()
    )
