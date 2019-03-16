# AWS_PROJECT

### Steps to run on Ubuntu
###### Setup 0.1
1. Spawn EC2 instance with Ubuntu and ssh into it. (this is tested on 18.04)
2. $ sudo apt-get update
3. $ sudo apt-get upgrade
4. $ sudo apt install supervisor
5. $ sudo apt install gunicorn
6. $ sudo apt-get install python3-pip
7. $ pip3 install pipenv
###### Setup 0.2
1. clone the repo and $ cd AWS-PROJECT
2. $ pipenv shell
3. $ cd aws-project-webapp
4. $ pip -r install requirements.txt
5. supervisord -c supervisord.conf
