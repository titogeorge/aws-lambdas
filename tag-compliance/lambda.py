import json
import pprint
import boto3

"""
Terminate instances that does not comply with organization Tag requirements.
Create an Cloudwatch rule with the below pattern and target the lambda
    EventPattern:
        detail-type:
          - AWS API Call via CloudTrail
        source:
          - aws.ec2
        detail:
          eventSource:
            - ec2.amazonaws.com
          eventName:
            - RunInstances        

"""

# Mandatory Tags with no restriction on value
MANDATORY_TAGS = ["Name", "created-by"]
# Mandatory Tags with restricted values
WHITE_LISTED_TAGS = {
    "application": ["web", "infra", "sap", "informatica"],
    "department": ["marketing", "finance"]
}

# Optionally get Tags from SSM parameter store
# ssm_client = boto3.client('ssm')
# man_tag_string = ssm_client.get_parameter(Name = "MANDATORY_TAGS")
# MANDATORY_TAGS = man_tag_string['Parameter']['Value'].split(",")


def lambda_handler(event, context):
    """
    Input Arguments:
    RunInstances event from Cloudwatch-CloudTrail
    """
    instances = []

    # Get instance ids from event
    for instance in event['detail']['responseElements']['instancesSet']['items']:
        instanceId = instance['instanceId']
        print("Checking tags for instance: " + instanceId)
        # Get Tag Set from instance
        tagMap = {}
        for tag in instance['tagSet']['items']:
            tagMap[tag["key"]] = tag["value"]

        invalid_tags = []
        # Iterate mandatory tags and see if it exists
        for man_tag in MANDATORY_TAGS:
            if man_tag not in tagMap:
                invalid_tags.append(man_tag)

        for key, value in WHITE_LISTED_TAGS.items():
            if key in tagMap:
                if tagMap[key] not in value:
                    invalid_tags.append(key)
            else:
                invalid_tags.append(key)

        print(invalid_tags)
        if invalid_tags:
            tagsStr = ', '.join(invalid_tags)
            response = "Following tags " + tagsStr + \
                " are missing for instance :"+instanceId
            print(response)
            # Terminate Instance, commented to avoid accidental termination
            # term_instance(instanceId)
            # Optional - publish to SNS
            # publish_invalid_tags(instanceId, response)


def term_instance(id):
    ec2 = boto3.client(
        'ec2',
        region_name='us-east-1'
    )
    response = ec2.terminate_instances(InstanceIds=[id])

    return


def publish_invalid_tags(instance_id, tag_response):

    client = boto3.client('sns')

    pub_response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789:MissingTagsTermInstanceSNSTopic',
        Message=tag_response,
        Subject='EC2 Tag Issue'
    )

    return
