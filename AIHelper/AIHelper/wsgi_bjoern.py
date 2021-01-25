import os
import sys
import site
import bjoern
import os, signal

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir("C:/Users/aiden/.conda/envs/battlefield/Lib/site-packages")




# Add the app's directory to the PYTHONPATH
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper')
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper/AIHelper')

os.environ['DJANGO_SETTINGS_MODULE'] = 'AIHelper.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AIHelper.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

NUM_WORKERS = 8
worker_pids = []

bjoern.listen(application, '0.0.0.0', 8000)
for _ in range(NUM_WORKERS):
    pid = os.fork()
    if pid > 0:
        # in master
        worker_pids.append(pid)
    elif pid == 0:
        # in worker
        try:
            bjoern.run()
        except KeyboardInterrupt:
            pass
        exit()

try:
   # Wait for the first worker to exit. They should never exit!
   # Once first is dead, kill the others and exit with error code.
    pid, xx = os.wait()
    worker_pids.remove(pid)
finally:
    for pid in worker_pids:
        os.kill(pid, signal.SIGINT)
        exit(1)