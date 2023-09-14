from flask import Flask
from flask_minify import Minify
from flask_log_request_id import RequestID
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['LOG_REQUEST_ID_LOG_ALL_REQUESTS'] = True
app.config['CHANNEL_NAME'] = 'telelug'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per minute", "50 per second"],
    storage_uri="memory://",
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
