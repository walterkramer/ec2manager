import boto3
import botocore
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
def cli():
    """ec2manager manages ec2's"""


@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--customer',default=None,
    help="Only snapshots for customer (tag Customer:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(customer, list_all):
    "List EC2 snapshots"

    instances = filter_instances(customer)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                   s.id,
                   v.id,
                   i.id,
                   s.state,
                   s.progress,
                   s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break

    return


@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--customer',default=None,
    help="Only volumes for customer (tag Customer:<name>)")

def list_volumes(customer):
    "List EC2 volumes"

    instances = filter_instances(customer)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"    
            )))
    return


@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snaphots of all volumes")
@click.option('--customer',default=None,
    help="Only instances for customer (tag Customer:<name>)")

def create_snapshots(customer):
    "Create snapshots for EC2 instances"

    instances = filter_instances(customer)
    
    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("Creating snapshot of volume {0} from instance {1}".format(v.id , i.id))
            v.create_snapshot(Description="Created by ec2manager")
        
        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done!")

    return

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
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Cloud not stop {0} .".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--customer',default=None,
    help="Only instances for customer (tag Customer:<name>)")

def start_instances(customer):
    "Start EC2 instances"
    
    instances = filter_instances(customer)
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Cloud not start {0} .".format(i.id) + str(e))
            continue
    return

if __name__ == '__main__':
    cli()


