#!flask/bin/python
import os
from flask import Flask
from flask import request
from flask import jsonify
from joblib import load
import boto3
import time
from datetime import datetime
app = Flask(__name__)


#********************************************************************
# SET UP QUEUE
#********************************************************************
def _create_queue():
    queue_client = boto3.client('sqs')
    # delete any previously existing queue with this name
    queues = queue_client.list_queues(QueueNamePrefix = 'aws-project-queue')
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
def _delete_queue_messages():
    queue_client = boto3.client('sqs')
    queues = queue_client.list_queues(QueueNamePrefix = 'aws-project-queue')
    time.sleep(5)
    # if queue exists
    count = 0
    if 'QueueUrls' in queues:
        while True:
            # adjust MaxNumberOfMessages if needed
            messages = queue_client.receive_message(QueueUrl = queues['QueueUrls'][0], MaxNumberOfMessages = 1) 
            # when the queue is exhausted, the response dict contains no 'Messages' key
            if 'Messages' in messages: 
                count += 1
                # 'Messages' is a list
                for message in messages['Messages']: 
                    # process the messages
                    print(message['Body'])
                    # next, we delete the message from the queue so no one else will process it again
                    queue_client.delete_message(QueueUrl = queues['QueueUrls'][0],ReceiptHandle = message['ReceiptHandle'])
            else:
                print('Queue is now empty')
                break
    return count

def _get_message_count(queue_url = 'https://sqs.us-west-1.amazonaws.com/138838165366/aws-project-queue'):
    client = boto3.client('sqs')
    response = client.get_queue_attributes(QueueUrl = queue_url, AttributeNames=['ApproximateNumberOfMessages'])
    return int(response['Attributes']['ApproximateNumberOfMessages'])

def _create_instance():
    ec2 = boto3.resource('ec2')
    user_data_script = """java -cp /home/ubuntu/darknet/deeplearning.jar com.cloud.CloudAWS"""
    user_data_script = """#!/bin/bash 
    /home/ubuntu/darknet/java_script.sh"""
    instance = ec2.create_instances(
        ImageId = 'ami-0d3d75415da9089c0',
        MinCount = 1,
        MaxCount = 1,
        InstanceType = 't2.micro',
        KeyName = 'aws-project-ec2-keypair',
        SecurityGroupIds = ['sg-05dd11dc93caae569'],
        TagSpecifications = [
                {
                        'ResourceType': 'instance',
                        'Tags': [
                                 {
                                         'Key': 'Name',
                                         'Value': 'elastic-instance'
                                 },
                         ]
                }],
        UserData = user_data_script
    )
    return instance[0].id

def _get_instances_count():
    ec2_client = boto3.resource('ec2')
    instances = ec2_client.instances.filter()
    count = 0
    for instance in instances:
        if instance.state["Name"] == "running":
            count += 1
    return count

def _scaling_logic(messages_count):
    instance_count = _get_instances_count()
    # replace 'if' with 'while' in the later stages of development
    count = 0
    if instance_count < messages_count and instance_count < 20:
        _create_instance()
        count += 1
    return count

def _get_file_contents_from_s3(file_name, bucket_name = 'clouddeeplearning'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    body = ""
    for obj in bucket.objects.all():
        key = obj.key
        if key.endswith(file_name):
            body = obj.get()['Body'].read()
            break
    if body: 
        body = body.decode("utf-8")
        body = body[1:-1]
    return body

#********************************************************************
# REST END POINTS
#********************************************************************

@app.route('/get_message_count', methods=['GET'])
def get_message_count_response():
    message_count = _get_message_count()
    return jsonify(return_value = "Approximately " + str(message_count) + " messages in the Queue!")

@app.route('/get_instance_count', methods=['GET'])
def get_instance_count_response():
    instance_count = _get_instances_count()
    return jsonify(return_value = str(instance_count) + " instances running!")


@app.route('/delete_queue_messages', methods=['GET'])
def delete_queue_messages_response():
    deleted_message_approx_count = _delete_queue_messages()
    # return jsonify(return_value = "Approximately " + str(max(deleted_message_approx_count - 10, 0)) + " to "+ str(max(deleted_message_approx_count, 10)) + " messages delete!")
    return jsonify(return_value = str(deleted_message_approx_count) + " messages deleted!")

@app.route('/', methods=['GET'])
def main_response():
    instance_id = 1#_create_instance()
    queue_client = boto3.client('sqs')
    queues = queue_client.list_queues(QueueNamePrefix='aws-project-queue')
    if 'QueueUrls' in queues and queues['QueueUrls']:
        messages_count = _get_message_count(queues['QueueUrls'][0])
        file_name = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')
        enqueue_response = queue_client.send_message(QueueUrl = queues['QueueUrls'][0], MessageBody = file_name)
        messages_count += 1
    else:
        return jsonify(return_value = "Queue Not Found, Try again!") 
    
    instances_created = _scaling_logic(messages_count)
    
    return_message = str(messages_count) + " messages in the Queue!"
    if instances_created:
        return_message += " Also created " + str(instances_created) + " instances."
   
    # considering video detection deeplearning model will run for at least 30 seconds
    time.sleep(30)
    file_contents = _get_file_contents_from_s3(file_name, bucket_name = "clouddeeplearning")
    while not file_contents:
        time.sleep(1)
        file_contents = _get_file_contents_from_s3(file_name, bucket_name = "clouddeeplearning")
   
    return_obj = {"message": return_message, "detected_object": file_contents.strip()}
    
    return jsonify(return_value = return_obj) 

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
