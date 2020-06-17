from lambdakube.sts_client_factory import STSClientFactory
from lambdakube.eks_client import EKSClient
from lambdakube.token_generator import TokenGenerator
from lambdakube.exceptions import LambdaKubeError
from kubernetes import client as client, config as kube_config
import botocore.session
import logging
import yaml

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def metadata(name=None, namespace=None, labels=None, annotations=None):
    return client.V1ObjectMeta(
        name=name,
        namespace=namespace,
        labels=labels,
        annotations=annotations,
    )


class LambdaKube(object):
    def __init__(self,
                 cluster_id,
                 region,
                 role_arn=None,
                 username=None,
                 session=botocore.session.get_session(),
                 kube_config_filepath='/tmp/kubeconfig'
                 ):
        self.cluster_id = cluster_id
        self.region = region
        self.role_arn = role_arn
        self.username = username
        self._session = session
        self._kube_config_filepath = kube_config_filepath

    def get_config(self):
        try:
            self.update_kubeconfig()
            return client.ApiClient(self._kube_client_configuration())
        except LambdaKubeError as e:
            logging.error(f'could not get config {e}')

    def update_kubeconfig(self):
        try:
            self._write_kubeconfig()
            kube_config.load_kube_config(self._kube_config_filepath)
        except LambdaKubeError as e:
            logging.error(f'could not update kubeconfig {e}')

    def _kube_client_configuration(self):
        """
        Return the kubernetes python client configuration
        """
        configuration = client.Configuration()
        configuration.api_key['authorization'] = self._get_token()
        configuration.api_key_prefix['authorization'] = 'Bearer'

        return configuration

    def _get_token(self):
        """
        Return bearer token
        """
        session = self._session

        client_factory = STSClientFactory(session)
        sts_client = client_factory.get_sts_client(
            region_name=self.region,
            role_arn=self.role_arn)
        token = TokenGenerator(sts_client).get_token(self.cluster_id)

        return token

    def _write_kubeconfig(self):
        """
        Write kubeconfig to filesystem
        """
        content = self._generate_kubeconfig()
        with open(self._kube_config_filepath, 'w') as outfile:
            yaml.dump(content, outfile, default_flow_style=False)

    def _generate_kubeconfig(self):
        """
        Return a dictionary containing the kubeconfig
        """
        cluster_info = self._cluster_info()
        certificate = cluster_info['certificateAuthority']['data']
        arn = cluster_info["arn"]
        endpoint = cluster_info['endpoint']

        return {
            'apiVersion': 'v1',
            'clusters': [
                {
                    'cluster':
                        {
                            'server': endpoint,
                            'certificate-authority-data': certificate
                        },
                    'name': arn

                }],
            'contexts': [
                {
                    'context':
                        {
                            'cluster': arn,
                            'user': arn,
                        },
                    'name': arn
                }
            ],
            'current-context': arn,
            'kind': 'Config',
            'preferences': {},
            'users': [
                {
                    'name': arn,
                    'user': {
                        'name': arn,
                    }
                }
            ]
        }

    def _cluster_info(self):
        """
        Return the EKS cluster info
        """
        return EKSClient(
            self._session,
            self.cluster_id
        ).get_cluster_info()['cluster']
