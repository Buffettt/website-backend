import os
import paramiko
import sys

if os.environ["TRAVIS_REPO_SLUG"] != "ChatTriggers/website-backend" or os.environ["TRAVIS_PULL_REQUEST"] != "false" or os.environ["TRAVIS_BRANCH"] != "master":
    sys.exit()

transport = paramiko.Transport((os.environ["SERVER_HOST"], 22))
transport.connect(username=os.environ["SERVER_USER"], password=os.environ["SERVER_PASS"])
sftp = paramiko.SFTPClient.from_transport(transport)
try:
    sftp.mkdir("/root/web")
except IOError:
    pass
sftp.put("build/libs/" + os.listdir("build/libs/")[0], "/root/web/server.jar")
sftp.close()

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=os.environ["SERVER_HOST"],username=os.environ["SERVER_USER"],password=os.environ["SERVER_PASS"])

stdin, stdout, stderr = ssh_client.exec_command("rm /root/web/server.log")  # Non-blocking call
stdout.channel.recv_exit_status()                                           # Blocking call

stdin, stdout, stderr = ssh_client.exec_command("killall java")             # Non-blocking call
stdout.channel.recv_exit_status()                                           # Blocking call

stdin, stdout, stderr = ssh_client.exec_command("cd /root/web; java -jar /root/web/server.jar --production > /root/web/server.log 2>&1 &")
stdout.channel.recv_exit_status()

ssh_client.close()