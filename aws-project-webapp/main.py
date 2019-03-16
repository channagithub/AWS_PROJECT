#!flask/bin/python
import os
from flask import Flask
from flask import request
from flask import jsonify
from joblib import load

app = Flask(__name__)

@app.route('/isAlive', methods=['GET'])
def index():
    return jsonify(return_value = "channa works on aws project")

if __name__ == "__main__":
    print("Loading!")
    app.run()
