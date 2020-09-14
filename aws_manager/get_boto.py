
import boto3

ec2 = boto3.resource('ec2')

reservations = ec2.get_all_instances(instance_ids=['i-029c2cafa57a111ea'])
instance = reservations[0].instances[0]
print(instance)