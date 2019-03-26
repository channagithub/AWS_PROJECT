import boto3
import utils

def _scaling_logic():
    messages_count = utils._get_message_count()
    instance_count = utils._get_instances_count()
    print("instance_count: ", instance_count)
    print("messages_count: ", messages_count)
    print()
    if (instance_count - 1) < messages_count and instance_count < 20:
        try:
            utils._create_instance()
            print("Created instance, currently ", utils._get_instances_count(), " instances running")
        except Exception as e:
            pass

if __name__ == '__main__':
    while True:
        _scaling_logic()
