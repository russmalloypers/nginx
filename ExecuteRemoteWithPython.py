#Requirements
#This is written for Python 3 (3.4+)
#Remote host should be Ubuntu16+ and it's assumed UFW is disabled
#On the execution host, must have paramiko module installed (sudo pip-3.6 install paramiko) and nginx.conf should be located at /tmp/nginx.conf
#The public IP used to execute this script must be added to the SSH whitelist for the host (currently hardcoded to 70.42.161.157)
#"curl ifconfig.co" to see your public IP. Current whitelisted IP's: 54.84.27.87(ec2 instance)

remotehost = '70.42.161.157'
un = 'root'
pw = 'In a hole in the ground there lived a hobbit.'

import paramiko
import sys 

class ExecuteSSH:
    ssh = ""
    def __init__(self, host_ip, uname, passwd):
        try:
            #print("before ssh connect")
            self.ssh = paramiko.SSHClient() #http://docs.paramiko.org/en/2.4/api/client.html
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #http://docs.paramiko.org/en/2.4/api/client.html fixes missing key
            self.ssh.connect(host_ip, username=un, password=pw)
            #print("after ssh connect")
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print(str(e)) #print exception if auth fails
            sys.exit(-1) #exit python
            
    def executecmd(self,cmd):
        try:
            channel = self.ssh.invoke_shell() #object being created using Paramiko module
            timeout = 60 #in seconds
            channel.settimeout(timeout)
            newline = '\r'
            channel.send(cmd + ' ; exit ' + newline) #send execute commands to remote channel object
            #output running commands to console
            line_buffer = ''
            channel_buffer = ''
            while True:
                channel_buffer = channel.recv(1).decode('UTF-8')
                if len(channel_buffer) == 0:
                    break
                channel_buffer = channel_buffer.replace('\r', '')
                if channel_buffer != '\n':
                    line_buffer += channel_buffer
                else:
                    print(line_buffer)
                    line_buffer = ''
        except paramiko.SSHException as e:
            print(str(e))
            sys.exit(-1)
    
    def uploadfile(self, src, dest):
        #receive source & destination in the case you wanted to upload multiple files
        #http://docs.paramiko.org/en/2.4/api/sftp.html#paramiko.sftp_client.SFTPClient
        ftp_client = self.ssh.open_sftp()
        ftp_client.put(src, dest)


#echo and save custom 404 page to var custom404
custom404 = '''echo "<h1 style='color:red'>This is my custom Error 404 page: Not found :-(</h1>" | sudo tee /usr/share/nginx/html/custom_404.html'''


#Create object "conn_obj" from class ExecuteSSH
conn_obj = ExecuteSSH(remotehost, un, pw)

#execute remote commands. System broadcast, update system, install nginx, start nginx on reboot
conn_obj.executecmd('wall "Modifying system"')
conn_obj.executecmd('apt-get update')
conn_obj.executecmd('apt-get install nginx -y')
conn_obj.executecmd('systemctl enable nginx')

#remove nginx.conf in preparation for new file put. Not necessary but cleaner
conn_obj.executecmd('rm /etc/nginx/nginx.conf') 

#write custom 404 html file to /usr/share/nginx/html/custom_404.html
conn_obj.executecmd(custom404)


#upload new nginx.conf file
sftp = conn_obj.uploadfile('/tmp/nginx.conf', '/etc/nginx/nginx.conf')

#Reload nginx configuration and post that update is complete
conn_obj.executecmd('systemctl reload nginx')
conn_obj.executecmd('wall "System update complete"')