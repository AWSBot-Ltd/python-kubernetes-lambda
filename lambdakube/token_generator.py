import base64

URL_TIMEOUT = 60
TOKEN_EXPIRATION_MINS = 14
TOKEN_PREFIX = 'k8s-aws-v1.'


class TokenGenerator(object):
    def __init__(self, sts_client):
        self._sts_client = sts_client

    def get_token(self, cluster_name):
        """ Generate a presigned url token to pass to kubectl. """
        url = self._get_presigned_url(cluster_name)
        token = TOKEN_PREFIX + base64.urlsafe_b64encode(
            url.encode('utf-8')).decode('utf-8').rstrip('=')
        return token

    def _get_presigned_url(self, cluster_name):
        return self._sts_client.generate_presigned_url(
            'get_caller_identity',
            Params={'ClusterName': cluster_name},
            ExpiresIn=URL_TIMEOUT,
            HttpMethod='GET',
        )
