"""This module contains some helpers for mocking eks clusters"""
from unittest.mock import patch
from mock import patch, Mock
from lambdakube.lambda_kube import LambdaKube
from botocore.session import get_session
import os
import unittest

from nose.tools import nottest


EXAMPLE_NAME = "ExampleCluster"
EXAMPLE_REGION = 'us-east-1'
EXAMPLE_USER = 'user@test.com'
EXAMPLE_ROLE_ARN = 'arn:aws:iam::012345678910:role/RoleArn'
EXAMPLE_DNS_DOMAIN = 'test.com'
EXAMPLE_VPC_ID = 'vpc-1234567890'


class BaseLambdaKubeTest(unittest.TestCase):
    def setUp(self):
        self.create_client_patch = patch(
            'botocore.session.Session.create_client'
        )
        self.mock_create_client = self.create_client_patch.start()
        self.session = get_session()
        self.client = Mock()
        self.client.describe_cluster.return_value = describe_cluster_response()
        self.client.generate_presigned_url.return_value = presigned_url()
        self.mock_create_client.return_value = self.client
        self.cluster_id = EXAMPLE_NAME
        self.region = EXAMPLE_REGION
        self.username = EXAMPLE_USER
        self.role_arn = EXAMPLE_ROLE_ARN
        self.dns_domain = EXAMPLE_DNS_DOMAIN
        self.vpc_id = EXAMPLE_VPC_ID

        self.lambdakube = LambdaKube(
            session=self.session,
            cluster_id=self.cluster_id,
            region=self.region,
            username=self.username
        )

        self.config = self.lambdakube.get_config()

@nottest
def get_testdata(file_name):
    """Get the path of a specific fixture"""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "testdata",
                        file_name)


def list_cluster_response():
    """Get an example list_cluster call (For mocking)"""
    return {
        "clusters": [
            EXAMPLE_NAME
        ]
    }


def describe_cluster_response():
    """Get an example describe_cluster call (For mocking)"""
    return {
        "cluster": {
            "status": "ACTIVE",
            "endpoint": "https://endpoint.amazonaws.com",
            "name": EXAMPLE_NAME,
            "certificateAuthority": {
                "data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpWR1Z6ZEdsdVp5QkVZWFJoRFFwVVpYTjBhVzVuSUVSaGRHRU5DbFJsYzNScGJtY2dSR0YwWVEwS2EzVmlaWEp1WlhSbGN6QWVGdzBLVkdWemRHbHVaeUJFWVhSaERRcFVaWE4wYVc1bklFUmhkR0ZWQkFNVERRcHJkV0psY201bGRHVnpNQUVpTUEwS1ZHVnpkR2x1WnlCRVlYUmhEUXBVWlhOMGFXNW5JRVJoZEdFTkNsUmxjM1JwYm1jZ1JHRjBZY3UvR1FnbmFTcDNZaHBDTWhGVVpYTjBhVzVuSUVSaGRHRXl3clZqeEpWNjNwNFVHRmpZdHdGR1drUldJVkV1VkdWemRHbHVaeUJFWVhSaGJzT0MxSVJiTDhPd0lpMVhiWGg2VkdWemRHbHVaeUJFWVhSaFpXVndTTk9VVUZKNmN5QWJaaFpnWVNkTUV3MEtGMVJsYzNScGJtY2dSR0YwWVFZRFZSMFBBUUVFQkFNQ0FsUmxjM1JwYm1jZ1JHRjBZUUV3RFFvR0NTcElEUXBVWlhOMGFXNW5JRVJoZEdGcEgxc1pPRTNMa3lrMU9DWUNHUloyTEZjM3paOCtHell3WEZSbGMzUnBibWNnUkdGMFlYMUR5NjFNMVlGV1AxWVRIMVJsYzNScGJtY2dSR0YwWVd0aE5oMVphM2dWUDBGaGNSWjdKaW9oZVc4N1JsUmxjM1JwYm1jZ1JHRjBZUVpIVHd4NE9IdzZmZz09DQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0t"
            },
            "roleArn": "arn:aws:iam::111222333444/eksRole",
            "resourcesVpcConfig": {
                "subnetIds": [
                    "subnet-00000000000000000",
                    "subnet-00000000000000001",
                    "subnet-00000000000000002"
                ],
                "vpcId": "vpc-00000000000000000",
                "securityGroupIds": [
                    "sg-00000000000000000"
                ]
            },
            "version": "1.10",
            "arn": "arn:aws:eks:region:111222333444:cluster/" + EXAMPLE_NAME,
            "createdAt": 1500000000.000
        }
    }

def describe_cluster_no_status_response():
    """Get an example describe_cluster call (For mocking)"""
    return {
        "cluster": {
            "endpoint": "https://endpoint.amazonaws.com",
            "name": EXAMPLE_NAME,
            "certificateAuthority": {
                "data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpWR1Z6ZEdsdVp5QkVZWFJoRFFwVVpYTjBhVzVuSUVSaGRHRU5DbFJsYzNScGJtY2dSR0YwWVEwS2EzVmlaWEp1WlhSbGN6QWVGdzBLVkdWemRHbHVaeUJFWVhSaERRcFVaWE4wYVc1bklFUmhkR0ZWQkFNVERRcHJkV0psY201bGRHVnpNQUVpTUEwS1ZHVnpkR2x1WnlCRVlYUmhEUXBVWlhOMGFXNW5JRVJoZEdFTkNsUmxjM1JwYm1jZ1JHRjBZY3UvR1FnbmFTcDNZaHBDTWhGVVpYTjBhVzVuSUVSaGRHRXl3clZqeEpWNjNwNFVHRmpZdHdGR1drUldJVkV1VkdWemRHbHVaeUJFWVhSaGJzT0MxSVJiTDhPd0lpMVhiWGg2VkdWemRHbHVaeUJFWVhSaFpXVndTTk9VVUZKNmN5QWJaaFpnWVNkTUV3MEtGMVJsYzNScGJtY2dSR0YwWVFZRFZSMFBBUUVFQkFNQ0FsUmxjM1JwYm1jZ1JHRjBZUUV3RFFvR0NTcElEUXBVWlhOMGFXNW5JRVJoZEdGcEgxc1pPRTNMa3lrMU9DWUNHUloyTEZjM3paOCtHell3WEZSbGMzUnBibWNnUkdGMFlYMUR5NjFNMVlGV1AxWVRIMVJsYzNScGJtY2dSR0YwWVd0aE5oMVphM2dWUDBGaGNSWjdKaW9oZVc4N1JsUmxjM1JwYm1jZ1JHRjBZUVpIVHd4NE9IdzZmZz09DQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0t"
            },
            "roleArn": "arn:aws:iam::111222333444/eksRole",
            "resourcesVpcConfig": {
                "subnetIds": [
                    "subnet-00000000000000000",
                    "subnet-00000000000000001",
                    "subnet-00000000000000002"
                ],
                "vpcId": "vpc-00000000000000000",
                "securityGroupIds": [
                    "sg-00000000000000000"
                ]
            },
            "version": "1.10",
            "arn": "arn:aws:eks:region:111222333444:cluster/" + EXAMPLE_NAME,
            "createdAt": 1500000000.000
        }
    }

def describe_cluster_creating_response():
    """Get an example describe_cluster call during creation"""
    return {
        "cluster": {
            "status": "CREATING",
            "name": EXAMPLE_NAME,
            "certificateAuthority": {},
            "roleArn": "arn:aws:iam::111222333444/eksRole",
            "resourcesVpcConfig": {
                "subnetIds": [
                    "subnet-00000000000000000",
                    "subnet-00000000000000001",
                    "subnet-00000000000000002"
                ],
                "vpcId": "vpc-00000000000000000",
                "securityGroupIds": [
                    "sg-00000000000000000"
                ]
            },
            "version": "1.10",
            "arn": "arn:aws:eks:region:111222333444:cluster/" + EXAMPLE_NAME,
            "createdAt": 1500000000.000
        }
    }


def describe_cluster_deleting_response():
    """Get an example describe_cluster call during deletion"""
    return {
        "cluster": {
            "status": "DELETING",
            "endpoint": "https://endpoint.amazonaws.com",
            "name": EXAMPLE_NAME,
            "certificateAuthority": {
                "data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpWR1Z6ZEdsdVp5QkVZWFJoRFFwVVpYTjBhVzVuSUVSaGRHRU5DbFJsYzNScGJtY2dSR0YwWVEwS2EzVmlaWEp1WlhSbGN6QWVGdzBLVkdWemRHbHVaeUJFWVhSaERRcFVaWE4wYVc1bklFUmhkR0ZWQkFNVERRcHJkV0psY201bGRHVnpNQUVpTUEwS1ZHVnpkR2x1WnlCRVlYUmhEUXBVWlhOMGFXNW5JRVJoZEdFTkNsUmxjM1JwYm1jZ1JHRjBZY3UvR1FnbmFTcDNZaHBDTWhGVVpYTjBhVzVuSUVSaGRHRXl3clZqeEpWNjNwNFVHRmpZdHdGR1drUldJVkV1VkdWemRHbHVaeUJFWVhSaGJzT0MxSVJiTDhPd0lpMVhiWGg2VkdWemRHbHVaeUJFWVhSaFpXVndTTk9VVUZKNmN5QWJaaFpnWVNkTUV3MEtGMVJsYzNScGJtY2dSR0YwWVFZRFZSMFBBUUVFQkFNQ0FsUmxjM1JwYm1jZ1JHRjBZUUV3RFFvR0NTcElEUXBVWlhOMGFXNW5JRVJoZEdGcEgxc1pPRTNMa3lrMU9DWUNHUloyTEZjM3paOCtHell3WEZSbGMzUnBibWNnUkdGMFlYMUR5NjFNMVlGV1AxWVRIMVJsYzNScGJtY2dSR0YwWVd0aE5oMVphM2dWUDBGaGNSWjdKaW9oZVc4N1JsUmxjM1JwYm1jZ1JHRjBZUVpIVHd4NE9IdzZmZz09DQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0t"
            },
            "roleArn": "arn:aws:iam::111222333444/eksRole",
            "resourcesVpcConfig": {
                "subnetIds": [
                    "subnet-00000000000000000",
                    "subnet-00000000000000001",
                    "subnet-00000000000000002"
                ],
                "vpcId": "vpc-00000000000000000",
                "securityGroupIds": [
                    "sg-00000000000000000"
                ]
            },
            "version": "1.10",
            "arn": "arn:aws:eks:region:111222333444:cluster/" + EXAMPLE_NAME,
            "createdAt": 1500000000.000
        }
    }


def presigned_url():
    """Return a string representing a presigned url"""
    return 'https://presignedurl.test.com'
