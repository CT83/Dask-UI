import boto3
import paramiko

ec2 = boto3.resource('ec2')
target_id = "i-0019cfe9227988d5e"

# Create the key pair
# create a file to store the key locally
# outfile = open('ec2-keypair.pem', 'w')
#
# # call the boto ec2 function to create a key pair
# key_pair = ec2.create_key_pair(KeyName='ec2-keypair')
#
# # capture the key and store it in a file
# KeyPairOut = str(key_pair.key_material)
# print(KeyPairOut)
# outfile.write(KeyPairOut)


# instances = ec2.create_instances(
#     ImageId='ami-06b263d6ceff0b3dd',
#     MinCount=1,
#     MaxCount=1,
#     InstanceType='t2.micro',
#     KeyName='ec2-keypair'
# )
#

instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print(instance.id, instance.instance_type)
    if instance.id == target_id:

        key = paramiko.RSAKey.from_private_key_file('ec2-keypair.pem')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect/ssh to an instance
        try:
            # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
            client.connect(hostname=instance.public_ip_address, username="ubuntu", pkey=key)

            # Execute a command(cmd) after connecting/ssh to an instance
            client.exec_command("touch /tmp/1")
            stdin, stdout, stderr = client.exec_command("ls /tmp")
            print(stdout.read().decode('utf-8'))

            # close the client connection once the job is done
            client.close()
            break

        except Exception as e:
            print(e)

