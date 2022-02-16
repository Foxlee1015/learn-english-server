import os
# https://docs.gunicorn.org/en/stable/settings.html
bind = f'0.0.0.0:{os.getenv("FLASK_PORT")}'
worker_class = 'sync' # default = sync
workers = 2 # default = 1
loglevel = 'debug'
accesslog = './logs/access.log'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog =  './logs/error.log'
capture_output = 'True' # for python print
