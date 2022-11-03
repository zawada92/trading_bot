import ast
import datetime
import redis
import simplejson as json

from collections.abc import Generator
from decimal import Decimal
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    Response,
    request,
    url_for,
)
from pandas import DataFrame

from bot_flask.auth import login_required
from bot_flask.dbutil import Notification, OhlcCandle, get_db, Contract
from trading_bot.gateio_utils import ExchangeApi

TREND_UP = 0
TREND_DOWN = 1

notification_bp = Blueprint(
    "notifications", __name__, url_prefix="/notifications"
)
red = redis.StrictRedis()


@notification_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    notifications = Notification.query.filter_by(
        user_id=g.user.id, is_active=True
    ).all()
    notifications_as_dict = [n.__dict__ for n in notifications]

    return render_template(
        "notifications/notifications.html", notifications=notifications_as_dict
    )


@notification_bp.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    notification = Notification.query.filter_by(id=id).first()

    if not notification.is_active:
        return redirect(url_for("notifications.index"))

    if request.method == "POST":
        price = request.form["price"]
        error = None

        if not price:
            error = "Price is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.app.logger.info(
                "Requested update notification price to {}".format(price)
            )
            price = Decimal(price.strip(' "'))
            notification.request_price = price

            if valid_notification(notification, notification.contract_name):
                db.session.commit()
            else:
                return render_template(
                    "notifications/update.html", notification=notification
                )

            return redirect(url_for("notifications.index"))

    return render_template(
        "notifications/update.html", notification=notification
    )


@notification_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    Notification.query.filter_by(id=id, user_id=g.user.id).delete()
    get_db().session.commit()
    return redirect(url_for("notifications.index"))


@notification_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        contract_str = request.form["contract"]
        trend = request.form["trend"]
        price = request.form["price"]

        error = validate_user_notification_input(contract_str, trend, price)

        if error is not None:
            flash(error)
        else:
            trend = int(trend)
            price = Decimal(price.strip(' "'))
            notification = create_and_validate_notification(
                contract_str, trend, price
            )
            if notification is not None:
                db = get_db()
                db.session.add(notification)
                db.session.commit()
                return redirect(url_for("notifications.index"))
            else:
                render_template("notifications/create.html")

    return render_template("notifications/create.html")


@notification_bp.route("/stream")
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


def event_stream() -> Generator:
    """Sends notification events with prepared data.

    Yields:
        str: Notification dict string
    """
    pubsub = red.pubsub()
    pubsub.subscribe("notifier")

    # TODO: handle client disconnection.
    for message in pubsub.listen():
        if message["type"] == "message":
            event_stream_str = message["data"].decode("utf-8")
            event_stream_dict = ast.literal_eval(event_stream_str)
            # User is lisening only for his notifications with
            # event type of "notify_+{username}"
            event_type = "notify_"
            event_type = event_type + str(event_stream_dict["user"])
            yield "event: {}\ndata: {}\n\n".format(
                event_type, str(event_stream_dict["message"])
            )


def job_fetch_and_notify() -> Response:
    """Fetches actual data from exchange and sends
    notifications if triggered.

    Returns:
        Response: Standard response returned
    """
    db = get_db()

    db.app.logger.info(
        "Job fetch_and_notify at time: {}".format(datetime.datetime.now())
    )
    exchange_api = ExchangeApi()

    for contract in db.contract_list:

        db_candles = (
            OhlcCandle.query.filter_by(contract_name=contract)
            .order_by(OhlcCandle.candle_id)
            .all()
        )
        df = DataFrame(
            exchange_api.get_candle_stick(
                contract=contract, interval="1m", limit=20
            )
        )

        current_price = Decimal(df["close"].iloc[-1])
        update_contract_current_price(contract, current_price)
        update_db_candles(db_candles, df)
        send_triggered_active_notifications(contract, current_price)

    db.session.commit()

    return Response(status=204)


def update_contract_current_price(
    contract: str, current_price: Decimal
) -> None:
    """Updates Contract object with current price.

    Params:
        contract(str): Contract object to be updated
        current_price(Decimal): Current contract price from exchange
    """
    contract_obj = Contract.query.filter_by(contract_name=contract).first()
    contract_obj.latest_price = contract_obj.current_price
    contract_obj.current_price = current_price


def update_db_candles(db_candles: OhlcCandle, df: DataFrame) -> None:
    """Updates OhlcCandle objects in database with current data.

    Params:
        db_candles(OhlcCandle): List of candles to be updated
        df(DataFrame): Current data from exchange
    """
    for index, row in df.iterrows():
        db_candles[index].time = datetime.datetime.strptime(
            row["time"], "%H:%M %d.%m.%y"
        )
        db_candles[index].open = row["open"]
        db_candles[index].high = row["high"]
        db_candles[index].low = row["low"]
        db_candles[index].close = row["close"]


def send_triggered_active_notifications(
    contract: str, current_price: Decimal
) -> None:
    """Sends active notification triggered with current price change.

    Params:
        contract(str): Contract name which related notifications will be sent
        current_price(Decimal): Current price of contract
    """
    active_notifications = (
        Notification.query.filter_by(is_active=True, contract_name=contract)
        .order_by(Notification.created)
        .all()
    )
    for notification in active_notifications:
        if (
            notification.trend == TREND_UP
            and notification.request_price < current_price
        ):
            send_notification(notification)

        if (
            notification.trend == TREND_DOWN
            and notification.request_price > current_price
        ):
            send_notification(notification)


def send_notification(notification: Notification) -> None:
    """Prepares information needed to send notification and publishes
    it on redis pubsub.

    Params:
        notification(Notification): Object of notification to be sent
    """
    notification.is_active = False
    message = str(notification.request_price)
    user = notification.user_id
    notification.issued = datetime.datetime.now()
    red.publish(
        "notifier",
        json.dumps({"type": "notify_", "message": message, "user": user}),
    )


def validate_user_notification_input(
    contract_str: str, trend: str, price: str
) -> str:
    """_summary_

    Params:
        contract_str(str): User input contract name
        trend(str): User input trend
        price(str): User input price

    Returns:
        str: Error message or None.
    """
    if not contract_str:
        return "Contract is required."
    if not trend:
        return "Trend is required."
    if not price:
        return "Price is required."
    return None


def create_and_validate_notification(
    contract_str: str, trend: int, price: Decimal
) -> Notification:
    """Creates notification instance and validates it.

    Params:
        contract_str(str): Contract name
        trend(int): Notification trend
        price(Decimal): Notification request price

    Returns:
        Notification: Validated notification
    """
    notification = Notification(
        user_id=g.user.id,
        is_active=True,
        contract_name=contract_str,
        trend=trend,
        request_price=price,
        created=datetime.datetime.now(),
    )
    if valid_notification(notification, contract_str):
        return notification

    return None


def valid_notification(notification: Notification, contract_str: str) -> bool:
    """_summary_

    Params:
        notification(Notification): Notification to validate
        contract_str(str): Contract name

    Returns:
        bool: True if valid notification False otherwise
    """
    contract = Contract.query.filter_by(contract_name=contract_str).first()
    if (
        contract.current_price > notification.request_price
        and notification.trend == TREND_UP
    ):
        flash(
            "With UP trend price must be higher than current: {}".format(
                contract.current_price
            )
        )
        return False

    if (
        contract.current_price < notification.request_price
        and notification.trend == TREND_DOWN
    ):
        flash(
            "With DOWN trend price must be lower than current: {}".format(
                contract.current_price
            )
        )
        return False

    return True
