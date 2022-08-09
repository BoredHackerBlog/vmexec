#requires python3, python3-pip, virtualbox
#pip packages required: flask, flask-sqlalchemy, flask-admin
#the host this is running on should be able to connect to VM's IP on port 8000
#running: flask run
#config: look for #CHANGME
from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
import time
import threading
import xmlrpc.client
import subprocess
import os

vboxmanage = "/usr/bin/VBoxManage" #CHANGME your vboxmanage binary, this should be default location on ubuntu
upload_folder = "/tmp/trash/upload" #CHANGME this is where uploaded files will go
download_folder = "/tmp/trash/download" #CHANGEME this is where artifacts are downloaded to

os.system("mkdir -p "+upload_folder) #this creates a folder for uploading files
os.system("mkdir -p "+download_folder)

max_vms_running = 1 #CHANGEME amount of VM's running at once

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 #CHANGME, max upload size, 50MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:?check_same_thread=False' #i think this is the correct way of using this
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asdflkajdsflkjasefiojel134234234' #CHANGEME

db = SQLAlchemy(app)

admin = Admin(app)

class VMStatus(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(15),nullable=False) # VM name
    ip = db.Column(db.String(15),nullable=False) # IP address of the VM, the host should be able to reach this on port 8000
    snapshot = db.Column(db.String(15),nullable=False) # name of the snapshot that should be used
    available = db.Column(db.Boolean)

class InputTask(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    filepath = db.Column(db.String(255),nullable=False) #source filepath for this task
    timeout = db.Column(db.Integer,nullable=False) #how long the VM will run after the file has been opened or executed
    vmname = db.Column(db.String(15),nullable=True) #specific VM this task should run on
    available = db.Column(db.Boolean)

db.create_all()

admin.add_view(ModelView(VMStatus, db.session))
admin.add_view(ModelView(InputTask, db.session))

#CHANGEME, add your VM's here
db.session.add(VMStatus(name="winVM",ip="192.168.56.101",snapshot="Snapshot5", available=True))
db.session.commit()

def vm_start(name, snapshot):
    proc = subprocess.Popen([vboxmanage,"snapshot",name,"restore",snapshot])
    proc.wait()
    proc = subprocess.Popen([vboxmanage,"startvm",name,"--type","gui"]) #CHANGEME this can be gui or headless
    proc.wait()

def vm_stop(name):
    proc = subprocess.Popen([vboxmanage,"controlvm",name,"poweroff"])
    proc.wait()

# this function runs as a thread and it's responsible for processing a task
def vm_process(vmid, taskid):
    task = InputTask.query.filter_by(id=taskid).first() # get task info
    vm = VMStatus.query.filter_by(id=vmid).first() # get vm info
    vm_start(vm.name, vm.snapshot) # start the VM
    conn = xmlrpc.client.ServerProxy('http://%s:8000'%(vm.ip)) # initiate xmlrpc client
    connected = False
    counter = 0
    while (connected == False) and (counter < 5): # try to connect and call the ping function or at least loop 6 times before exiting the loop
        try:
            if conn.ping() == True:
                connected = True
        except:
            time.sleep(5)
            counter = counter+1
    if connected == True: # if calling ping() was successful then send file, open or execute file, and finally sleep until timeout time runs out
        with open(task.filepath, "rb") as handle:
            binary_data = xmlrpc.client.Binary(handle.read())
        filename = task.filepath.split('/')[-1]
        conn.upload_file("C:/%s"%(filename),binary_data)
        conn.start_aurora()
        time.sleep(60) # this needs to be changed depending on how long it takes for aurora to start based on the system resources and config used
        conn.execute("C:/%s"%(filename))
        time.sleep(task.timeout)
        time.sleep(10) #seems like if the timeout time is too small then evtx will be empty
        dl_filepath = download_folder+"/"+str(vmid)+"_"+str(taskid)+"_"+str(time.time())+".json"
        with open(dl_filepath, "wb") as handle:
            handle.write(conn.download_file("C:/aurora_logs.json").data)
    vm_stop(vm.name) # stop the VM
    vm.available = True
    db.session.commit()

def task_processor():
    while True:
        tasks = InputTask.query.filter_by(available=True).all() # get all the tasks
        vms_available_count = VMStatus.query.filter_by(available=True).count() # find out what VMs are available for use
        vms_running_count = VMStatus.query.filter_by(available=False).count() # find out what's running
        #if we have available tasks, available VM's, and less than max VM's running
        if (len(tasks) > 0) and (vms_available_count > 0) and (vms_running_count < max_vms_running):
            #go through each task and if any is can be started then start 
            for task in tasks:
                # if vm non-vm-specific, then start
                if task.vmname == None:
                    vm = VMStatus.query.filter_by(available=True).first()
                    vm.available = False
                    task.available = False
                    db.session.commit()
                    vm_process_thread = threading.Thread(target=vm_process, args=(vm.id, task.id))
                    vm_process_thread.start()
                    del vm #there was a bug and this fixes it. idk what im doing tbh. bug was that task 2 and 3 started uploading and opening files in the same running VM.
                    break
                # if vm specific then find vm, then start
                elif task.vmname != None:
                    vm = VMStatus.query.filter_by(available=True, name=task.vmname).first()
                    if vm != None:
                        vm.available = False
                        task.available = False
                        db.session.commit()
                        vm_process_thread = threading.Thread(target=vm_process, args=(vm.id, task.id))
                        vm_process_thread.start()
                        del vm
                        break
        time.sleep(10)

@app.route('/', methods = ['POST','GET']) # GET request to get an upload form and post will add a task
def webui_upload():
    if request.method == 'GET':
        vmnames = []
        vmnames.append("Any")
        for vmname in VMStatus.query.with_entities(VMStatus.name).all():
            vmnames.append(vmname[0])

        form = """
<html>
<body>
<form action = '/' method="POST" enctype="multipart/form-data">
File: <input type="file" name="file" /> <br>
VM: <select name="vmname">
{% for vmname in vmnames %}
<option value="{{ vmname }}"> {{ vmname }}</option>
{% endfor %}
</select> <br>
Time(seconds): <input type="number" name="timeout" value=60> <br>
<input type="submit" />
</form>
</body>
</html>
        """
        return render_template_string(form,vmnames=vmnames)
    if request.method == 'POST':
        if request.files['file'].filename != '':
            f = request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            filepath = (os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            timeout = request.form['timeout']
            vmname = request.form['vmname']
            if vmname == 'Any':
                db.session.add(InputTask(filepath=filepath,timeout=timeout,available=True))
                db.session.commit()
            else:
                db.session.add(InputTask(filepath=filepath,timeout=timeout,available=True,vmname=vmname))
                db.session.commit()
            return "Task added"
        else:
            return "You didn't upload a file"

task_processor_run = threading.Thread(target=task_processor, daemon=True)
task_processor_run.start()

if __name__ == '__main__':
    app.run(debug=False)
