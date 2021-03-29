# vmexec (work in progress)
This project takes in a file via webui, runs a VM, puts the file on the VM, and opens/executes the file (think cuckoo/cape sandbox but without any analysis at all)

# Use case
This project is similar (well only the VM start/stop and file upload open/execute parts) to cuckoo or cape sandbox but I don't need any deep analysis or any of the advanced features both of those provide. I just wanted to open files in a VM (any available or specific one) without getting anything in return from the VM. 

One of the use cases is to forward logs from the VM's to somewhere else and just open/execute file in it. The VM's can also contain EDR/AV solutions which can be used for analysis of the file.

# Technologies
- Python3
- Virtualbox
- Flask
- Flask-SQLAlchemy
- Flask-Admin
- Tested with Ubuntu 20.04

# Running the project
- Clone/download the project
- Install packages and libraries
- Create a VM, set static ip, intall python3+, disable firewall, run agent.py as an admin, and take a snapshot with agent.py running (your host should able to access port 8000 on guest VM)
- Modify the code, look for #CHANGEME
- Run "flask run" from project directory and visit localhost:5000 in your browser.

# Modifying the project
agent.py (which will be running in the VM) can be modified by editing the MyFuncs class and adding more functions. Check Python3 xmlrpc documentation.

vm_process function, in app.py, is pretty much the main function that does everything such as starting the VM, uploading a file, opening/executing a file, and stopping the VM. This is where you can add more functions to either do things inside the VM or outside the VM. This function runs as a thread when a task is being processed.

# Warning
- The webapp doesn't have any protection and neither does agent, anyone can schedule tasks and execute commands if they can access the webui or agent
- Code doesn't have the best error handling, things may crash once in a while
- If you're dealing with malware, remember to isolate stuff or route traffic correctly...

# Resources
I usually try to do a good job of documenting where I got code or ideas from either in the code or outside but I didn't this time. I looked at Cuckoo and Cape sandbox design and code (they use http agent, i decided to use xmlrpc cuz less code :D). I also took ideas and partial code from various python tutorial sites, python documentation, and stackoverflow.
