#!flask/bin/python
import os
from flask import Flask
from flask import request
from flask import jsonify
from joblib import load
import boto3
import time
from datetime import datetime
from random import randint
import utils

app = Flask(__name__)

def _scaling_logic():
    messages_count = utils._get_message_count()
    instance_count = utils._get_instances_count()
    # replace 'if' with 'while' in the later stages of development
    count = 0
    while instance_count - 1 < messages_count and instance_count < 20 and count <= 5:
        count += 1
    # if instance_count - 1 < messages_count and instance_count < 20:
        try:
            utils._create_instance()

            messages_count = utils._get_message_count()
            instance_count = utils._get_instances_count()
        except Exception as e:
            instance_count = utils._get_instances_count()
            messages_count = utils._get_message_count()

    return instance_count

#********************************************************************
# REST END POINTS
#********************************************************************

@app.route('/get_message_count', methods=['GET'])
def get_message_count_response():
    message_count = utils._get_message_count()
    return jsonify(return_value = "Approximately " + str(message_count) + " messages in the Queue!")

@app.route('/get_instance_count', methods=['GET'])
def get_instance_count_response():
    instance_count = utils._get_instances_count()
    return jsonify(return_value = str(instance_count) + " instances running!")


@app.route('/delete_queue_messages', methods=['GET'])
def delete_queue_messages_response():
    deleted_message_approx_count = utils._delete_queue_messages()
    # return jsonify(return_value = "Approximately " + str(max(deleted_message_approx_count - 10, 0)) + " to "+ str(max(deleted_message_approx_count, 10)) + " messages delete!")
    return jsonify(return_value = str(deleted_message_approx_count) + " messages deleted!")

@app.route('/', methods=['GET'])
def main_response():
    queue_client = boto3.client('sqs')
    queues = queue_client.list_queues(QueueNamePrefix='aws-project-queue')
    if 'QueueUrls' in queues and queues['QueueUrls']:
        messages_count = utils._get_message_count(queues['QueueUrls'][0])
        file_name = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')
        file_name += '-' + str(randint(0, 9000000000000))
        enqueue_response = queue_client.send_message(QueueUrl = queues['QueueUrls'][0], MessageBody = file_name)
        messages_count += 1
    else:
        return jsonify(return_value = "Queue Not Found, Try again!") 
    
    # instances_created = _scaling_logic()
    
    return_message = str(messages_count) + " messages in the Queue!"
    # if instances_created:
        # return_message += " Also created " + str(instances_created) + " instances."
   
    # considering video detection deeplearning model will run for at least 30 seconds
    time.sleep(30)
    file_contents = utils._get_file_contents_from_s3(file_name, bucket_name = "clouddeeplearning")
    while not file_contents:
        time.sleep(1)
        file_contents = utils._get_file_contents_from_s3(file_name, bucket_name = "clouddeeplearning")
   
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
