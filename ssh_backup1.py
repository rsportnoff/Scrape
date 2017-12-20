import paramiko
from scp import SCPClient

def ssh(chosen, input, client, k):
    client.connect(hostname=chosen+".compute-1.amazonaws.com", username="ubuntu", pkey=k)
    command = "sudo python parse_other.py " + input
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    sftp = client.open_sftp()
    sftp.get('/home/ubuntu/results','/home/ubuntu/results_bu1')
    sftp.get('/home/ubuntu/ccie13_log','/home/ubuntu/bu1_log')
    sftp.close()
    client.close()

def do(urls,chosen):
    k = paramiko.RSAKey.from_private_key_file("/home/ubuntu/.ssh/backpage2-scraper.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    input = "\"" + str(urls)+"\""
    ssh(chosen, input, client, k)