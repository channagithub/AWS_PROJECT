# AWS_PROJECT

### Steps to run on Ubuntu
0.1. Spawn EC2 instance with Ubuntu and ssh into it. (this is tested on 18.04)
0.2. $ sudo apt-get update
0.3. $ sudo apt-get upgrade
0.4. $ sudo apt install supervisor
0.5. $ sudo apt install gunicorn
0.6. $ sudo apt-get install python3-pip
0.7. $ pip3 install pipenv
1. clone the repo and $ cd AWS-PROJECT
2. $ pipenv shell
3. $ cd aws-project-webapp
4. $ pip -r install requirements.txt
5. supervisord -c supervisord.conf
