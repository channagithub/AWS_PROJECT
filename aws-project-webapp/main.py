#!flask/bin/python
import os
from flask import Flask
from flask import request
from flask import jsonify
from joblib import load
import boto3

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def main_response():
    instance_id = _create_instance()
    return jsonify(return_value = instance_id) 

if __name__ == "__main__":
    print("Loading!")
    app.run()
