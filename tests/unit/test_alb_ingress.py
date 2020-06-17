from lambdakube.alb_ingress import ALBIngress
from tests.unit.test_utils import BaseLambdaKubeTest
from mock import Mock


class ALBIngressTest(BaseLambdaKubeTest):
    def setUp(self):
        super(ALBIngressTest, self).setUp()
        self.name = 'alb-ingress-controller'
        self.namespace = 'kube-system'
        self.alb_ingress = ALBIngress(
            configuration=self.config,
            role_arn=self.role_arn,
            cluster_name=self.cluster_id,
            vpc_id=self.vpc_id,
            region=self.region,
        )
        self.kube_client = Mock()
        type(self.alb_ingress).apps_v1_api = self.kube_client
        type(self.alb_ingress).core_v1_api = self.kube_client
        type(self.alb_ingress).rbac_v1_api = self.kube_client

    def test_create(self):
        response = self.alb_ingress.create()
        self.assertEqual(len(response), 4)

    def test_patch(self):
        response = self.alb_ingress.create()
        self.assertEqual(len(response), 4)

    def test_delete(self):
        response = self.alb_ingress.create()
        self.assertEqual(len(response), 4)

    def test_deployment(self):
        args = [
            '--ingress-class=alb',
            f'--cluster-name={self.cluster_id}',
            f'--aws-vpc-id={self.vpc_id}',
            f'--aws-region={self.region}',
        ]
        response = self.alb_ingress._deployment()
        self.assertEqual(response.api_version, 'apps/v1')
        self.assertEqual(response.kind, 'Deployment')
        self.assertTrue(response.metadata)
        self.assertEqual(response.spec.template.spec.containers[0].image,
                    'docker.io/amazon/aws-alb-ingress-controller:v1.1.4')
        self.assertEqual(response.spec.template.spec.containers[0].args, args)

    def test_service_account(self):
        annotations = dict({'eks.amazonaws.com/role-arn': self.role_arn})
        response = self.alb_ingress._service_account()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ServiceAccount')
        self.assertEqual(response.metadata.annotations, annotations)

    def test_cluster_role(self):
        response = self.alb_ingress._cluster_role()
        self.assertEqual(response.api_version, 'rbac.authorization.k8s.io/v1')
        self.assertEqual(response.kind, 'ClusterRole')
        self.assertTrue(response.metadata)
        self.assertTrue(response.rules)

    def test_cluster_role_binding(self):
        response = self.alb_ingress._cluster_role_binding()
        self.assertEqual(response.kind, 'ClusterRoleBinding')
        self.assertEqual(response.metadata.name, 'alb-ingress-controller')
        self.assertEqual(response.role_ref.api_group,
                         'rbac.authorization.k8s.io')
        self.assertEqual(response.role_ref.kind, 'ClusterRole')
        self.assertEqual(response.role_ref.name, self.name)
        self.assertEqual(response.subjects[0].api_group, None)
        self.assertEqual(response.subjects[0].kind, 'ServiceAccount')
        self.assertEqual(response.subjects[0].name, self.name)
        self.assertEqual(response.subjects[0].namespace, self.namespace)