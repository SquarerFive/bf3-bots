"""
WSGI config for AIHelper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os



from django.core.wsgi import get_wsgi_application

import threading
import socket
import socketserver

import os
import site 
import sys
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper')
sys.path.append('C:/Users/aiden/Documents/Battlefield 3/Server/AIHelper/AIHelper')
os.environ['DJANGO_SETTINGS_MODULE'] = 'AIHelper.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AIHelper.settings')

application = get_wsgi_application()

# import navigation
from bots.utilities import behaviour
# from navigation.views import update_level_socket

# os.system("conda activate battlefield")
#site.addsitedir("C:/Users/aiden/.conda/envs/battlefield/Lib/site-packages")


# from cheroot import wsgi


class GlobalCache:
    result = None

class SocketTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.result = None
        super().__init__(request, client_address, server)
    
    

    def handle(self):
        self.length = self.request.recv(1024).strip()
        self.length = int(self.length.decode('utf-8'))
        #print('length: ', self.length)
        
        if GlobalCache.result != None:
            self.request.sendall(
                str.encode(f'00{len(GlobalCache.result)}')
            )
        
        self.data = self.request.recv(self.length).decode('utf-8').strip()
        #print('{} wrote: '.format(self.client_address[0]))
        #print(self.data)
        # # GlobalCache.result = update_level_socket(self.data)
        print(GlobalCache.result)
        
        
        self.request.send(
            str.encode(GlobalCache.result)
        )


class SocketApplication():
    def __init__(self):
        # setup
        
        self.host, self.port = "127.0.0.1", 2929
        # self.socket.listen(5)
        self.should_stop = False
    def listen(self):
        with socketserver.TCPServer((self.host, self.port), SocketTCPHandler) as server:
            server.serve_forever()



socket_app = SocketApplication()

tr = threading.Thread(target=socket_app.listen)
tr.start()


#


def my_crazy_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return [b'Hello world!']


#addr = '127.0.0.1', 8000
#server = wsgi.Server(addr, application)
#print("Starting")
#server.start()