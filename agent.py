#setup for xmlrpc
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import zipfile
import subprocess
from os.path import basename
import glob

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

        def start_aurora(self):
            subprocess.Popen(["start", "start_aurora.bat"], shell=True)
            return True

        #allows the host to upload file to VM
        def upload_file(self, filepath, filedata):
            with open(filepath, "wb") as handle:
                handle.write(filedata.data)
            return True

        #allow host to download file from the vm
        def download_file(self, filepath):
            with open(filepath, "rb") as handle:
                return xmlrpc.client.Binary(handle.read())
        
        #execute or start a file, this should open whatever file type uploaded with default app
        def execute(self, filepath):
            subprocess.Popen(["start",filepath],shell=True)
            return True

    server.register_instance(MyFuncs())

    server.serve_forever()
