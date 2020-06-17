from lambdakube.lambda_kube import (
    LambdaKube, metadata
)
from tests.unit.test_utils import BaseLambdaKubeTest


class LambdaKubeTest(BaseLambdaKubeTest):
    def setUp(self):
        super(LambdaKubeTest, self).setUp()
        self.lambdakube = LambdaKube(
            session=self.session,
            cluster_id=self.cluster_id,
            region=self.region,
            username=self.username
        )
        self.name = 'lambdakube'
        self.namespace = 'default'

    def test_get_config(self):
        config = self.lambdakube.get_config()
        self.assertIn(
            'k8s-aws-v1.',
            config.configuration.api_key['authorization']
        )

    def test_metadata(self):
        labels = dict({'key': 'value'})
        response = metadata(
            name=self.name,
            namespace=self.namespace,
            labels=labels,
            annotations=None
        )
        self.assertEqual(response.name, self.name)
        self.assertEqual(response.namespace, self.namespace)
        self.assertEqual(response.labels, labels)
        self.assertEqual(response.annotations, None)
