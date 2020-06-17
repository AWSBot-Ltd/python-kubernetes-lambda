# LambdaKube
![Tests](https://github.com/lensesio-dev/python-lambdakube/workflows/Tests/badge.svg)

A toolkit for configuring AWS EKS with lambda functions and Kubernetes clients

## Example
```python
import os
from lambdakube import LambdaKube
from lambdakube.external_dns import ExternalDNS
from lambdakube.alb_ingress import ALBIngress


def handler(event, context):

    CLUSTER_ID = os.environ['EKS_CLUSTER_NAME']
    AWS_REGION = os.environ['AWS_DEFAULT_REGION']
    USERNAME   = os.environ['LAMBDA_EXECUTION_ROLE_ARN']
    DNS_DOMAIN = os.envron['DNS_DOMAIN']
    EXTERNAL_DNS_CONTROLLER_ROLE_ARN = os.envron['EXTERNAL_DNS_CONTROLLER_ROLE_ARN']
    ALB_INGRESS_CONTROLLER_ROLE_ARN = os.envron['ALB_INGRESS_CONTROLLER_ROLE_ARN']
    VPC_ID = os.envron['VPC_ID']

    configuration = LambdaKube(
        cluster_id=CLUSTER_ID,
        region=AWS_REGION,
        username=USERNAME
    ).get_config()

    response = ExternalDNS(
        configuration=configuration,
        role_arn=EXTERNAL_DNS_CONTROLLER_ROLE_ARN,
        dns_domain=DNS_DOMAIN
    ).create()
    
    print(response)

    response = ALBIngress(
        configuration=configuration,
        role_arn=ALB_INGRESS_CONTROLLER_ROLE_ARN,
        cluster_name=CLUSTER_ID,
        region=AWS_REGION,
        vpc_id=VPC_ID,
    ).create()

    print(response)
```
