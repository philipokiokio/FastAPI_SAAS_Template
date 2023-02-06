from celery import Celery
from celery.schedules import crontab

job = Celery("SAAS Template", broker="redis://localhost:6379/0")
job.conf.enable_utc = True
