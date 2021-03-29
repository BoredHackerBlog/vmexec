#setup for xmlrpc
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import subprocess

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

with SimpleXMLRPCServer(('0.0.0.0', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    #Myfuncs (copied from python's documentation :D)
    class MyFuncs:
        #just to see if connection is working or not/if VM is up or not
        def ping(self):
            return True
        
        #allows the host to upload file to VM
        def upload_file(self, filepath, filedata):
            with open(filepath, "wb") as handle:
                handle.write(filedata.data)
                return True
        
        #execute or start a file, this should open whatever file type uploaded with default app
        def execute(self, filepath):
            subprocess.Popen(["start",filepath],shell=True)
            return True

    server.register_instance(MyFuncs())

    server.serve_forever()