import threading
import time

import boto3
import paramiko


class Brain:

    def __init__(self, security_group):
        self.security_group = security_group
        self.key_pair = 'ec2-keypair'

    def _create_pem(self):
        ec2 = boto3.resource('ec2')

        # create a file to store the key locally
        outfile = open(self.key_pair + '.pem', 'w')

        # call the boto ec2 function to create a key pair
        key_pair = ec2.create_key_pair(KeyName=self.key_pair)

        # capture the key and store it in a file
        key_pair_out = str(key_pair.key_material)
        print(key_pair_out)
        outfile.write(key_pair_out)

    def _create_ec2(self):
        ec2 = boto3.resource('ec2')
        instances = ec2.create_instances(
            ImageId='ami-06b263d6ceff0b3dd',
            MinCount=1, MaxCount=1,
            InstanceType='t2.micro',
            KeyName=self.key_pair,
            SecurityGroups=[self.security_group])
        instance_id = instances[0].instance_id
        print("Created {}...".format(instance_id))
        print("Sleeping for 2 mins...")
        time.sleep(120)
        return instance_id

    def _run_ssh(self, instance_id, command):
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            print(instance.id, instance.instance_type)
            if instance.id == instance_id:
                key = paramiko.RSAKey.from_private_key_file(self.key_pair + '.pem')
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                client.connect(hostname=instance.public_ip_address, username="ubuntu", pkey=key)

                stdin, stdout, stderr = client.exec_command(
                    "sudo apt-get update -y && sudo apt-get install python3-pip -y && sudo pip3 install dask distributed bokeh")
                print(stdout.read().decode('utf-8'))
                print("Running SSH on {} - {}".format(instance_id, command))
                threading.Thread(target=client.exec_command, args=([command])).start()
                time.sleep(2)
                return instance.public_ip_address

    def main(self):
        sch_ip = self.setup_scheduler()
        # sch_ip = "54.166.246.77"
        worker_url = self.setup_worker(sch_ip)
        url = "http://{}:8787".format(sch_ip)
        print("Your Dask Scheduler is at {}".format(url))
        print(worker_url)
        return url

    def setup_scheduler(self, ):
        target_id = self._create_ec2()
        # command = "sudo apt-get update -y && sudo apt-get install python3-pip -y && sudo python3 -m pip install dask distributed bokeh && "
        command = "nohup dask-scheduler &"
        ip = self._run_ssh(instance_id=target_id, command=command)
        print(ip)
        return ip

    def setup_worker(self, scheduler_ip):
        target_id = self._create_ec2()
        # command = "sudo apt-get update -y && sudo apt-get install python3-pip -y && sudo python3 -m pip install dask distributed && "
        # command = "nohup dask-worker tcp://{}:8786 &".format(scheduler_ip)
        command = " (nohup dask-worker tcp://{}:8786 > /dev/null )".format(scheduler_ip)
        ip = self._run_ssh(instance_id=target_id, command=command)
        return ip


if __name__ == "__main__":
    brain = Brain(security_group='VeryBadSecurity')
    brain.main()
