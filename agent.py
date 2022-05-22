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
        
        def clean_logs(self):
            logs = ["security", "system", "microsoft-windows-powershell/operational", "microsoft-windows-sysmon/operational"]
            for alog in logs:
                subprocess.Popen(["wevtutil","cl",alog],shell=True)
            return True

        def start_wlb(self):
            subprocess.Popen(["c:/winlogbeat.exe", "-c", "c:/winlogbeat.yml"], shell=True)
            return True

        #zip files together for collection
        def collect(self):
            files = ['C:/windows/system32/winevt/logs/Microsoft-Windows-Powershell%4Operational.evtx', 'C:/windows/system32/winevt/logs/System.evtx','C:/windows/system32/winevt/logs/Security.evtx','C:/windows/system32/winevt/logs/Microsoft-Windows-Sysmon%4Operational.evtx']
            files = files + glob.glob("C:/winlogbeat*.ndjson")
            with zipfile.ZipFile("C:/collection.zip", mode="w") as archive:
                for afile in files:
                    try:
                        archive.write(afile, basename(afile))
                    except:
                        print("not found:", afile)
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
