import logging
import os
from lambdakube.lambda_kube import LambdaKube
from lambdakube.external_dns import ExternalDNS
import lambdakube.cfn_response as cfnresponse

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
            ExternalDNS(
                configuration=configuration,
                role_arn=os.environ['EXTERNAL_DNS_CONTROLLER_ROLE_ARN'],
                dns_domain=os.environ['DNS_DOMAIN']
            ).create()
            status = cfnresponse.SUCCESS
        elif event['RequestType'] == 'Update':
            logging.info(event['RequestType'])
            ExternalDNS(
                configuration=configuration,
                role_arn=os.environ['EXTERNAL_DNS_CONTROLLER_ROLE_ARN'],
                dns_domain=os.environ['DNS_DOMAIN']
            ).patch()
            status = cfnresponse.SUCCESS
        elif event['RequestType'] == 'Delete':
            logging.info(event['RequestType'])
            ExternalDNS(
                configuration=configuration,
                role_arn=os.environ['EXTERNAL_DNS_CONTROLLER_ROLE_ARN'],
                dns_domain=os.environ['DNS_DOMAIN']
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

