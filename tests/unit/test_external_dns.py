from lambdakube.external_dns import ExternalDNS
from tests.unit.test_utils import BaseLambdaKubeTest
from mock import Mock


class ExternalDNSTest(BaseLambdaKubeTest):
    def setUp(self):
        super(ExternalDNSTest, self).setUp()
        self.name = 'external-dns'
        self.namespace = 'kube-system'
        self.external_dns = ExternalDNS(
            configuration=self.config,
            role_arn=self.role_arn,
            dns_domain=self.dns_domain
        )
        self.kube_client = Mock()
        type(self.external_dns).apps_v1_api = self.kube_client
        type(self.external_dns).core_v1_api = self.kube_client
        type(self.external_dns).rbac_v1_api = self.kube_client

    def test_create(self):
        response = self.external_dns.create()
        self.assertEqual(len(response), 4)

    def test_patch(self):
        response = self.external_dns.create()
        self.assertEqual(len(response), 4)

    def test_delete(self):
        response = self.external_dns.create()
        self.assertEqual(len(response), 4)

    def test_cluster_role(self):
        response = self.external_dns._cluster_role()
        self.assertEqual(response.api_version, 'rbac.authorization.k8s.io/v1beta1')
        self.assertEqual(response.kind, 'ClusterRole')
        self.assertTrue(response.metadata)
        self.assertTrue(response.rules)

    def test_service_account(self):
        annotations = dict({'eks.amazonaws.com/role-arn': self.role_arn})
        response = self.external_dns._service_account()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ServiceAccount')
        self.assertEqual(response.metadata.annotations, annotations)

    def test_deployment(self):
        annotations = dict({'iam.amazonaws.com/role': self.role_arn})
        args = [
            '--source=service',
            '--source=ingress',
            f'--domain-filter={self.dns_domain}',
            '--provider=aws',
            '--registry=txt',
            '--txt-owner-id=hostedzone-identifier',
        ]
        response = self.external_dns._deployment()
        self.assertEqual(response.api_version, 'apps/v1')
        self.assertEqual(response.kind, 'Deployment')
        self.assertTrue(response.metadata)
        self.assertEqual(response.spec.template.metadata.annotations,
                         annotations)
        self.assertEqual(response.spec.strategy.type, 'Recreate')
        self.assertEqual(response.spec.template.spec.security_context.fs_group,
                         65534)
        self.assertEqual(response.spec.template.spec.containers.image,
                    'registry.opensource.zalan.do/teapot/external-dns:latest')
        self.assertEqual(response.spec.template.spec.containers.args, args)

    def test_cluster_role_binding(self):
        response = self.external_dns._cluster_role_binding()
        self.assertEqual(response.kind, 'ClusterRoleBinding')
        self.assertEqual(response.metadata.name, f'{self.name}-viewer')
        self.assertEqual(response.role_ref.api_group,
                         'rbac.authorization.k8s.io')
        self.assertEqual(response.role_ref.kind, 'ClusterRole')
        self.assertEqual(response.role_ref.name, self.name)
        self.assertEqual(response.subjects[0].api_group, None)
        self.assertEqual(response.subjects[0].kind, 'ServiceAccount')
        self.assertEqual(response.subjects[0].name, self.name)
        self.assertEqual(response.subjects[0].namespace, self.namespace)