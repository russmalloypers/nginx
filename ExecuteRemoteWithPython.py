remotehost = '70.42.161.157'
un = 'root'
pw = 'Password123'

import paramiko
import sys 

class ExecuteSSH:
    ssh = ""
    def __init__(self, host_ip, uname, passwd):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host_ip, username=un, password=pw)
            print("XXX = inside init function")
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print(str(e))
            
    def executecmd(self,cmd):
        try:
            channel = self.ssh.invoke_shell()
            timeout = 60 #in seconds
            channel.settimeout(timeout)
            newline = '\r'
            line_buffer = ''
            channel_buffer = ''
            channel.send(cmd + ' ; exit ' + newline)
            while True:
                channel_buffer = channel.recv(1).decode('UTF-8')
                if len(channel_buffer) == 0:
                    break
                channel_buffer = channel_buffer.replace('\r', '')
                if channel_buffer != '\n':
                    line_buffer += channel_buffer
                else:
                    print(line_buffer + 'RM')
                    line_buffer = ''
        except paramiko.SSHException as e:
            print(str(e))
            sys.exit(-1)
    
    def uploadfile(self,location): #update this to take both source and dest. as input - i think it will look better
        ftp_client = self.ssh.open_sftp()
        #ftp_client.put(str(location), '/tmp/')
        #ftp_client.close()
        source= '/tmp/nginx.conf'
        destination = location
        #print(ftp_client.listdir('/tmp')) #works!, listed the /tmp directory http://docs.paramiko.org/en/2.4/api/sftp.html#paramiko.sftp_client.SFTPClient
        ftp_client.put(source, destination)

#echo and save custom 404 page to var custom404
custom404 = '''echo "<h1 style='color:red'>This is my custom Error 404 page: Not found :-(</h1>" | sudo tee /usr/share/nginx/html/custom_404.html'''

#Create object "conn_obj" from class ExecuteSSH
conn_obj = ExecuteSSH(remotehost, un, pw)

#execute remote commands. System broadcast, update system, install nginx, start nginx on reboot
conn_obj.executecmd('wall "Modifying system"')
conn_obj.executecmd('apt-get update')
conn_obj.executecmd('apt-get install nginx -y')
conn_obj.executecmd('systemctl enable nginx')

#remove nginx.conf in preparation for new file put
conn_obj.executecmd('rm /etc/nginx/nginx.conf') 

#write custom 404 html file to /usr/share/nginx/html/custom_404.html
conn_obj.executecmd(custom404)


#upload new nginx.conf file
sftp = conn_obj.uploadfile('/etc/nginx/nginx.conf')

#Reload nginx configuration and post that update is complete
conn_obj.executecmd('systemctl reload nginx')
conn_obj.executecmd('wall "System update complete"')