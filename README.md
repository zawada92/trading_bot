AUTOMATED TRADING BOT

Test execution:
/home/zawada/projects/trading_bot/env/bin/python -m unittest tests.test_strategy_hammer

Bot start command:
/home/zawada/projects/trading_bot/env/bin/python /home/zawada/projects/trading_bot/trading_bot/bot.py

Activate environment:
    source /home/zawada/projects/trading_bot/env/bin/activate
To initialize database:
    export FLASK_APP=bot_flask
    flask init-db
To start with gunicorn:
    gunicorn --worker-class=gevent -t 99999 "bot_flask:create_app()"

To debug in VSCode add below configuration to launch.json:
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


