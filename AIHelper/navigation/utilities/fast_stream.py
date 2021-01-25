import threading
import socket
import socketserver
import random

class GlobalCache:
    result = None

g_GlobalCache = GlobalCache()

class SocketTCPHandler(socketserver.BaseRequestHandler):
    # def __init__(self, request, client_address, server):
    #     self.result = None
    #     # self.r = server.r
    #     super().__init__(request, client_address, server)
        
        

    def handle(self):
        global g_GlobalCache
        self.inital = (self.request.recv(4)).strip()
        #print(self.inital)
        #self.length = int(self.length.decode('utf-8'))
        #print('length: ', self.length)
        # print("Test")
        # print(self.r)
        #print("req")
        if g_GlobalCache.result != None:
            # print(g_GlobalCache.result)
            self.request.sendall(
                str.encode(g_GlobalCache.result)
            )
        # self.server.__shutdown_request = True
        
        


class SocketApplication():
    def __init__(self):
        # setup
        self.server = None
        self.host, self.port = "127.0.0.1", 2929
        # self.socket.listen(5)
        self.should_stop = False
        self.server = None
    def set_port(self):
        self.port = random.randint(2929, 3939)
    def listen(self):
        #if self.server:
        #    self.server.shutdown()

        self.server = socketserver.TCPServer((self.host, self.port), SocketTCPHandler)
        print("opened on ", self.host, self.port)
        # self.server.r = g_GlobalCache.result
            
        #self.server.serve_forever()

socket_app = SocketApplication()
#socket_app.set_port()
#socket_app.listen()
global_socket_thread = None#threading.Thread(target = socket_app.server.serve_forever)
try:
   # global_socket_thread.start()
   pass
except:
    pass

def start_socket_thread(in_data):
    global global_socket_thread
    global g_GlobalCache
    global socket_app
    
    # if socket_app.server:
    #     socket_app.server.server_close()
    #     socket_app.server.shutdown()
    #    # print("shutdown")

    g_GlobalCache.result = in_data
    
    #global_socket_thread = threading.Thread(target = socket_app.server.serve_forever)
    

def stop_socket_thread():
    global global_socket_thread
    #socket_app.server.server_close()
    #
    #socket_app.server.shutdown()
    #global_socket_thread.join()