import boto3
import click

session = boto3.Session(profile_name='ec2manager')
ec2 = session.resource('ec2')

def filter_instances(customer):
    instances = []

    if customer:
        filters = [{'Name':'tag:Customer', 'Values':[customer]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--customer',default=None,
    help="Only instances for customer (tag Customer:<name>)")

def list_instances(customer):
    "List EC2 instances"

    instances = filter_instances(customer)
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            tags.get('Name', '<no name>'),
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            tags.get('Customer', '<no customername>'))))
    return

@instances.command('stop')
@click.option('--customer',default=None,
    help="Only instances for customer (tag Customer:<name>)")

def stop_instances(customer):
    "Stop EC2 instances"
    
    instances = filter_instances(customer)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
    return

@instances.command('start')
@click.option('--customer',default=None,
    help="Only instances for customer (tag Customer:<name>)")

def start_instances(customer):
    "Start EC2 instances"
    
    instances = filter_instances(customer)
    for i in instances:
        print("Starting {0}...".format(i.id))
        i.start()
    return

if __name__ == '__main__':
    instances()


