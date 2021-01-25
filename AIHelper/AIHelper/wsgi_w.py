import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir("C:/Users/aiden/.conda/envs/battlefield/Lib/site-packages")




# Add the app's directory to the PYTHONPATH
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper')
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper/AIHelper')

os.environ['DJANGO_SETTINGS_MODULE'] = 'AIHelper.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AIHelper.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()