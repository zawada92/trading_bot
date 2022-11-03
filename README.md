# Automated Trading Bot

## General
It is fun project for Python experience. Started as a command line tool (bot) for automated trading with usage of implemented strategies and data from crypto currency exchanges.
Then with time it is turned into web application, still under development. With many ideas on new functionalities, and highly variable requirements created on the fly. Main goal is to get familiar with Python technologies and OOP and eventually start automated trading (not only on crypto but also on stocks).

## Technologies
* Flask
* Bootstrap 5
* Sqlite
* SSE (Server Sent Events)
* Redis
* SQLAlchemy

Dependency
* pandas
* gate_api (Gateio API)
* ta (Technical Analysis library)
* flask_apscheduler
* redis (Server Sent Events using Redis pubsub)

### Current functionalities of web interface
* User notifications about crypto currency price
  * Create, Update, Delete notifications
* Show currency OHLC charts (even for not logged in viewers)

### Current functionalities of bot tool
* Use a hammer strategy on OHLC charts for set of crypto currencies to provide signals for potential trades

### TODOs
* Change Sqlite to PostgreSQL. The other supports Decimal.
* Prepare setup.py, setup.cfg etc.
* Learn more about database and cron jobs best practices.
* Extend functionalities of both web interface and bot tool
* Tests, tests, tests.... (Work In Progress)
* Use Swagger for routes documentation
* ...And many more...

## Developer info

### Web application
To initialize database:
```
$ export FLASK_APP=bot_flask
$ flask init-db
```

To start with gunicorn:
```
$ gunicorn --worker-class=gevent -t 99999 "bot_flask:create_app()"
```

To debug in VSCode add below configuration to launch.json:
```
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            "program": "${workspaceRoot}/web_bot/bot_flask/__init__.py",
            "env": {
                "FLASK_APP": "${workspaceRoot}/web_bot/bot_flask/__init__.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1",
                "PYTHONPATH":"${workspaceRoot}"
            },
            "args": [
                "run"
            ],
            "envFile": "${workspaceRoot}/.env",
            "jinja": true
        }
    ]
```

### python tool
Test execution:
```
$ python -m unittest tests.test_strategy_hammer
```

Bot start command:
```
$ python ./trading_bot/bot.py
```
