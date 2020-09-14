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
        time.sleep(5)
        while True:
            instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            instances = list(instances)
            a = instances[0]
            if a.state["Name"] != "running":
                time.sleep(1)
            else:
                time.sleep(60)
                break
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

                stdin, stdout, stderr = client.exec_command(command)
                print(stdout.read().decode('utf-8'))

                client.close()
                return instance.public_ip_address

    def main(self):
        sch_ip = brain.setup_scheduler()
        brain.setup_worker(sch_ip)

    def setup_scheduler(self, ):
        target_id = self._create_ec2()
        command = "sudo apt-get update -y && sudo apt-get install python3-pip -y && sudo python3 -m pip install dask distributed &&"
        command += "dask-scheduler"
        ip = self._run_ssh(instance_id=target_id, command=command)
        print(ip)
        return ip

    def setup_worker(self, scheduler_ip):
        target_id = self._create_ec2()
        command = "sudo apt-get update -y && sudo apt-get install python3-pip -y && sudo python3 -m pip install dask distributed &&"
        command += "dask-worker tcp://{}:8786".format(scheduler_ip)
        ip = self._run_ssh(instance_id=target_id, command=command)
        return ip


if __name__ == "__main__":
    brain = Brain(security_group='VeryBadSecurity')
    brain.main()
