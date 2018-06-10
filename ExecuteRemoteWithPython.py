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
            channel.send(cmd + ' ; exit ' + newline)
        except paramiko.SSHException as e:
            print(str(e))
            sys.exit(-1)

