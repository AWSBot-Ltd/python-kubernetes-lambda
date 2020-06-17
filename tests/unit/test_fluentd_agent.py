from lambdakube.fluentd_agent import FluentdAgent
from tests.unit.test_utils import BaseLambdaKubeTest
from mock import Mock
import hashlib


class FluentdAgentTest(BaseLambdaKubeTest):
    def setUp(self):
        super(FluentdAgentTest, self).setUp()
        self.name = 'alb-ingress-controller'
        self.namespace = 'kube-system'
        self.fluentd_agent = FluentdAgent(
            configuration=self.config,
            cluster_name=self.cluster_id,
            region=self.region,
        )
        self.kube_client = Mock()
        type(self.fluentd_agent).apps_v1_api = self.kube_client
        type(self.fluentd_agent).core_v1_api = self.kube_client
        type(self.fluentd_agent).rbac_v1_api = self.kube_client
        self.name = 'fluentd'
        self.namespace = 'amazon-cloudwatch'
        self.image = 'fluent/fluentd-kubernetes-daemonset:v1.7.3-debian-cloudwatch-1.0'

    def test_create(self):
        response = self.fluentd_agent.create()
        self.assertEqual(len(response), 6)

    def test_patch(self):
        response = self.fluentd_agent.create()
        self.assertEqual(len(response), 6)

    def test_delete(self):
        response = self.fluentd_agent.create()
        self.assertEqual(len(response), 6)

    def test_namespace(self):
        response = self.fluentd_agent._namespace()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'Namespace')
        self.assertEqual(response.metadata.name, self.namespace)

    def test_daemon_set(self):
        response = self.fluentd_agent._daemon_set()
        self.assertEqual(response.api_version, 'apps/v1')
        self.assertEqual(response.kind, 'DaemonSet')
        self.assertTrue(response.metadata)
        self.assertEqual(response.spec.template.spec.containers[0].image,
                   self.image)
        self.assertEqual(response.spec.template.spec.containers[0].env[0].name,
                         'REGION')
        self.assertEqual(response.spec.template.spec.containers[0].env[0].value,
                         'us-east-1')
        self.assertEqual(response.spec.template.spec.containers[0].env[1].name,
                         'CLUSTER_NAME')
        self.assertEqual(response.spec.template.spec.containers[0].env[1].value,
                         'ExampleCluster')
        self.assertEqual(response.spec.template.spec.containers[0].env[2].name,
                         'CI_VERSION')
        self.assertEqual(response.spec.template.spec.containers[0].env[2].value,
                         'k8s/1.1.1')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[0].name,
                         'config-volume')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[0].mount_path,
                         '/config-volume')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].name,
                         'fluentdconf')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].mount_path,
                         '/fluentd/etc')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].read_only,
                         None)
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].name,
                         'varlibdockercontainers')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].mount_path,
                         '/var/lib/docker/containers')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].name,
                         'runlogjournal')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].mount_path,
                         '/run/log/journal')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].name,
                         'dmesg')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].mount_path,
                         '/var/log/dmesg')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].read_only,
                         'true')

    def test_configmap(self):
        response = self.fluentd_agent._configmap()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ConfigMap')
        hasher = hashlib.md5()
        hasher.update(response.data['fluent.conf'].encode('utf-8'))
        self.assertEqual(hasher.hexdigest(),
                         '44df92e5c58ed0f3c3cfae187e12214a')
        hasher = hashlib.md5()
        hasher.update(response.data['containers.conf'].encode('utf-8'))
        self.assertEqual(hasher.hexdigest(),
                         '8d3f87932a9af8f483d161c8f9ce124a')
        hasher = hashlib.md5()
        hasher.update(response.data['host.conf'].encode('utf-8'))
        self.assertEqual(hasher.hexdigest(),
                         '10dcc488b3f6b5a8474bd3ae2fa35f79')
        hasher = hashlib.md5()
        hasher.update(response.data['systemd.conf'].encode('utf-8'))
        self.assertEqual(hasher.hexdigest(),
                         '2029049da516354ec69a80e1c42c92c5')

    def test_service_account(self):
        response = self.fluentd_agent._service_account()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ServiceAccount')

    def test_cluster_role(self):
        response = self.fluentd_agent._cluster_role()
        self.assertEqual(response.api_version, 'rbac.authorization.k8s.io/v1')
        self.assertEqual(response.kind, 'ClusterRole')
        self.assertTrue(response.metadata)
        self.assertTrue(response.rules)

    def test_cluster_role_binding(self):
        response = self.fluentd_agent._cluster_role_binding()
        self.assertEqual(response.kind, 'ClusterRoleBinding')
        self.assertEqual(response.metadata.name, f'{self.name}-role-binding')
        self.assertEqual(response.role_ref.api_group,
                         'rbac.authorization.k8s.io')
        self.assertEqual(response.role_ref.kind, 'ClusterRole')
        self.assertEqual(response.role_ref.name, f'{self.name}-role')
        self.assertEqual(response.subjects[0].api_group, None)
        self.assertEqual(response.subjects[0].kind, 'ServiceAccount')
        self.assertEqual(response.subjects[0].name, self.name)
        self.assertEqual(response.subjects[0].namespace, self.namespace)
