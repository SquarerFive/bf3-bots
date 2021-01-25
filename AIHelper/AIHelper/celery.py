import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'AIHelper.settings')

app : Celery = Celery('AIHelper')

app.config_from_object('django.conf:settings', namespace="CELERY")

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(1.0, hello.s("world"), name='test 1')

app.control.purge()

app.autodiscover_tasks()

@app.task(bind=True)
def test(self):
    print(f"hi {self.request!r}")

@app.task
def hello(arg):
    print(arg)