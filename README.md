# vmexec
This project takes in a file via webui, runs a VM, puts the file on the VM, and opens/executes the file (think cuckoo/cape sandbox but without any analysis at all) and also gets evtx files

blog post: http://www.boredhackerblog.info/2021/04/creating-malware-sandbox-for-sysmon-and.html (old, use this https://github.com/BoredHackerBlog/vmexec/tree/8fadb26c93244c02ee5d4c1f9c95769650035842 )

# Use case
This project is similar (well only the VM start/stop and file upload open/execute parts) to cuckoo or cape sandbox but I don't need any deep analysis or any of the advanced features both of those provide. I just wanted to open files in a VM (any available or specific one) and get evtx files and json event data. 

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
- Create a Windows VM or download IE VM
- Set static IP that host can access (i recommend adding host-only adapter)
- disable firewall, disable antivirus
- enable process and powershell logging by running the following as admin
```
echo Enabling process and command line auditing
auditpol /Set /subcategory:"Process Creation" /Success:Enable
auditpol /Set /subcategory:"Process Termination" /Success:Enable
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit\ /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1

echo Enabling powershell logging and transcript
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging\ModuleNames" /v * /t REG_SZ /d * /f /reg:64
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 00000001 /f /reg:64
```
- install sysmon and use the following configuration https://github.com/olafhartong/sysmon-modular/blob/master/sysmonconfig.xml
- download and put winlogbeat.exe in c:\ and use winlogbeat.yml thats in this repo in c:\
- install any other software you need (Office, Adobe, etc...) and 
- put agent.py in the VM and run it as an admin then take a snapshot
- add VM info and snapshot info to app.py (find #CHANGEME)
- Modify the code, look for #CHANGEME
- Run "flask run" or "python3 app.py" from project directory and visit localhost:5000 in your browser.

# Using command line
```
curl 'http://X.X.X.X:5000/' -X 'POST' -F "file=@test.bat" -F "timeout=60" -F "vmname=Any"
```

# Modifying the project
agent.py (which will be running in the VM) can be modified by editing the MyFuncs class and adding more functions. Check Python3 xmlrpc documentation.

vm_process function, in app.py, is pretty much the main function that does everything such as starting the VM, uploading a file, opening/executing a file, and stopping the VM. This is where you can add more functions to either do things inside the VM or outside the VM. This function runs as a thread when a task is being processed.

# Warning
- The webapp doesn't have any protection and neither does agent, anyone can schedule tasks and execute commands if they can access the webui or agent
- Code doesn't have the best error handling, things may crash once in a while
- If you're dealing with malware, remember to isolate stuff or route traffic correctly...

# Resources
I usually try to do a good job of documenting where I got code or ideas from either in the code or outside but I didn't this time. I looked at Cuckoo and Cape sandbox design and code (they use http agent, i decided to use xmlrpc cuz less code :D). I also took ideas and partial code from various python tutorial sites, python documentation, and stackoverflow.
