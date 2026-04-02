# gunicorn.conf.py
# Production server configuration for Render deployment

import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker processes
# 2-4 x number of CPU cores is a good rule of thumb
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
worker_class = "sync"

# Timeouts
timeout = 120          # LLM calls can be slow — give them 2 minutes
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"        # stdout
errorlog = "-"         # stderr
loglevel = os.getenv("LOG_LEVEL", "info")

# Reload in development (don't use in production)
reload = os.getenv("FLASK_ENV") == "development"
