import os
import sentry_sdk

from flask import Flask
from werkzeug.routing import BaseConverter

from sentry_sdk.integrations.flask import FlaskIntegration

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_log_request_id import RequestID
from flask_minify import Minify

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
app.config['LOG_REQUEST_ID_LOG_ALL_REQUESTS'] = True
app.config['CHANNEL_NAME'] = 'telelug'


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["360 per minute", "65 per second"],
    storage_uri="memory://" or os.getenv("REDIS_URL") or os.getenv("MONGODB_URL"),
    # Redis
    # storage_uri="redis://localhost:6379",
    # Redis cluster
    # storage_uri="redis+cluster://localhost:7000,localhost:7001,localhost:70002",
    # Memcached
    # storage_uri="memcached://localhost:11211",
    # Memcached Cluster
    # storage_uri="memcached://localhost:11211,localhost:11212,localhost:11213",
    # MongoDB
    # storage_uri="mongodb://localhost:27017",
    strategy="fixed-window",  # or "moving-window"
)

RequestID(app)
Minify(app)

import modules
