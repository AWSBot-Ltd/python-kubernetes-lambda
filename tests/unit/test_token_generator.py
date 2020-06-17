from unittest.mock import patch
import botocore.session
from lambdakube.token_generator import TokenGenerator
import unittest


class BaseTokenTest(unittest.TestCase):
    def setUp(self):
        self._session = botocore.session.get_session()
        self._access_key = 'ABCDEFGHIJKLMNOPQRST'
        self._secret_key = 'TSRQPONMLKJUHGFEDCBA'
        self._region = 'us-west-2'
        self._cluster_name = 'MyCluster'
        self._session.set_credentials(self._access_key, self._secret_key)
        self._sts_client = self._session.create_client('sts', self._region)


class TestTokenGenerator(BaseTokenTest):
    @patch.object(TokenGenerator, '_get_presigned_url', return_value='aHR0cHM6Ly9zdHMuYW1hem9uYXdzLmNvbS8=')
    def test_token_no_padding(self, mock_presigned_url):
        generator = TokenGenerator(self._sts_client)
        tok = generator.get_token(self._cluster_name)
        self.assertTrue('=' not in tok)