import sys

bind = "0.0.0.0:3000"
workers = 1
timeout = 120 
# Logging configuration
capture_output = True
loglevel = 'info'
accesslog = '-'  # stdout
errorlog = '-'   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Ensure logs go to stdout/stderr
logger_class = 'gunicorn.glogging.Logger'

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)