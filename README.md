# ec2manager

Demo project to manage AWS EC2 instances

## About

This project is a demo, and uses boto3 to manage AWS EC2 intances.

## Configuring

ec2manager uses the configuration file created by the AWS configure cli.
Create profile ec2manager for the access key

'aws configure --profile ec2manager'

## Running

'pipenv run python manager/ec2manager.py <command> <--customer=CustomerName>'

*command* is list, start, or stop
*project* is optional (default is none)


