import logging
import os
from lambdakube.lambda_kube import LambdaKube
from lambdakube.cloudwatch_agent import CloudWatchAgent
import lambdakube.cfn_response as cfnresponse
import json

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    print(event)
    configuration = LambdaKube(
        cluster_id=os.environ['EKS_CLUSTER_NAME'],
        region=os.environ['AWS_DEFAULT_REGION'],
        username=os.environ['LAMBDA_EXECUTION_ROLE_ARN']
    ).get_config()
    try:
        if event['RequestType'] == 'Create':
            logging.info(event['RequestType'])
            CloudWatchAgent(
                configuration=configuration,
                cluster_name=os.environ['EKS_CLUSTER_NAME'],
                region=os.environ['AWS_DEFAULT_REGION'],
            ).create()
            status = cfnresponse.SUCCESS
        elif event['RequestType'] == 'Update':
            logging.info(event['RequestType'])
            CloudWatchAgent(
                configuration=configuration,
                cluster_name=os.environ['EKS_CLUSTER_NAME'],
                region=os.environ['AWS_DEFAULT_REGION'],
            ).patch()
            status = cfnresponse.SUCCESS
        elif event['RequestType'] == 'Delete':
            logging.info(event['RequestType'])
            CloudWatchAgent(
                configuration=configuration,
                cluster_name=os.environ['EKS_CLUSTER_NAME'],
                region=os.environ['AWS_DEFAULT_REGION'],
            ).delete()
            status = cfnresponse.SUCCESS
        else:
            logging.error('Unhandled exception', exc_info=True)
            status = cfnresponse.FAILED
    except Exception as e:
        logging.error(f'Unhandled exception {e}', exc_info=True)
        status = cfnresponse.FAILED
    finally:
        cfnresponse.send(event, context, status, {})


if __name__ == "__main__":
    event = json.loads(open("create.event.json", 'r').read())
    handler(event, "")
