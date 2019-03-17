#!flask/bin/python
import os
from flask import Flask
from flask import request
from flask import jsonify
from joblib import load
import boto3
import time

app = Flask(__name__)


#********************************************************************
# SET UP QUEUE
#********************************************************************
def _create_queue():
    queue_client = boto3.client('sqs')
    # delete any previously existing queue with this name
    queues = queue_client.list_queues(QueueNamePrefix='aws-project-queue')
    time.sleep(5)
    # trying to delete only if it exists
    if 'QueueUrls' in queues:
        queue_client.delete_queue(QueueUrl = queues['QueueUrls'][0])
        # AWS restriction to wait for 60s before recreating queue with same name
        time.sleep(60)
    # create new queue
    queue_client.create_queue(QueueName='aws-project-queue')
    time.sleep(5)
    queues = queue_client.list_queues(QueueNamePrefix='aws-project-queue')
    time.sleep(5)
    # set up queue_url, this queue_url will be used further during rest calls to push messages/requests
    # queue_url is a list (easier to check when the app is live)
    queue_url = []
    if 'QueueUrls' in queues:
        queue_url = queues['QueueUrls']


#********************************************************************
# UTILITY FUNCTIONS
#********************************************************************

def _get_message_count(queue_client, queue_url):
    count = 0
    response = queue_client.receive_message(QueueUrl=queue_url)
    while 'Messages' in response:
        count += 1
        response = queue_client.receive_message(QueueUrl=queue_url)
    return count

def _create_instance():
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId = 'ami-0e355297545de2f82',
        MinCount = 1,
        MaxCount = 1,
        InstanceType = 't2.micro',
        KeyName = 'aws-project-ec2-keypair', 
    )
    return instance[0].id

#********************************************************************
# REST END POINTS
#********************************************************************
@app.route('/', methods=['GET'])
def main_response():
    instance_id = 1#_create_instance()
    queue_client = boto3.client('sqs')
    queues = queue_client.list_queues(QueueNamePrefix='aws-project-queue')
    if 'QueueUrls' in queues and queues['QueueUrls']:
        messages_count = _get_message_count(queue_client, queues['QueueUrls'][0])
        time.sleep(5)
        enqueue_response = queue_client.send_message(QueueUrl = queues['QueueUrls'][0], MessageBody='This is test message ' )
        messages_count += 1
    else:
        return jsonify(return_value = "Queue Not Found, Try again!") 
     

    return jsonify(return_value = messages_count) 

if __name__ == "__main__":
    print("Loading!")
    app.run()


## another way to access queue, but not able to count messages in queue with this method
# sqs = boto3.resource('sqs')
# queue = sqs.get_queue_by_name(QueueName='aws-project-queue')
# if queue.url:
#     enqueue_response = queue.send_message(QueueUrl = queue.url, MessageBody='This is test message ' )
# else:
#     return jsonify(return_value = "Queue Not Found, Try again!")
