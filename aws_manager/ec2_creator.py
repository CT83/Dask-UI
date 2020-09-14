import boto3


class EC2_Creator():
    pass


ec2 = boto3.resource('ec2')

instances = ec2.create_instances(
    ImageId='ami-06b263d6ceff0b3dd',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='ec2-keypair',
    SecurityGroups=['VeryBadSecurity']
)
a = instances
print(instances[0].instance_id)
