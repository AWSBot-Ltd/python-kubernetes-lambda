import json

from lambdakube.cloudwatch_agent import CloudWatchAgent
from tests.unit.test_utils import BaseLambdaKubeTest
from mock import Mock


class CloudWatchAgentTest(BaseLambdaKubeTest):
    def setUp(self):
        super(CloudWatchAgentTest, self).setUp()
        self.name = 'alb-ingress-controller'
        self.namespace = 'kube-system'
        self.cloudwatch_agent = CloudWatchAgent(
            configuration=self.config,
            cluster_name=self.cluster_id,
            region=self.region,
        )
        self.kube_client = Mock()
        type(self.cloudwatch_agent).apps_v1_api = self.kube_client
        type(self.cloudwatch_agent).core_v1_api = self.kube_client
        type(self.cloudwatch_agent).rbac_v1_api = self.kube_client
        self.name = 'cloudwatch-agent'
        self.namespace = 'amazon-cloudwatch'

    def test_create(self):
        response = self.cloudwatch_agent.create()
        self.assertEqual(len(response), 6)

    def test_patch(self):
        response = self.cloudwatch_agent.create()
        self.assertEqual(len(response), 6)

    def test_delete(self):
        response = self.cloudwatch_agent.create()
        self.assertEqual(len(response), 6)

    def test_namespace(self):
        response = self.cloudwatch_agent._namespace()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'Namespace')
        self.assertEqual(response.metadata.name, self.namespace)

    def test_daemon_set(self):
        response = self.cloudwatch_agent._daemon_set()
        self.assertEqual(response.api_version, 'apps/v1')
        self.assertEqual(response.kind, 'DaemonSet')
        self.assertTrue(response.metadata)
        self.assertEqual(response.spec.template.spec.containers[0].image,
                    'amazon/cloudwatch-agent:1.245315.0')
        self.assertEqual(response.spec.template.spec.containers[0].env[0].name,
                         'HOST_IP')
        self.assertEqual(response.spec.template.spec.containers[0].env[0].value,
                         None)
        self.assertEqual(response.spec.template.spec.containers[0].env[1].name,
                         'HOST_NAME')
        self.assertEqual(response.spec.template.spec.containers[0].env[1].value,
                         None)
        self.assertEqual(response.spec.template.spec.containers[0].env[2].name,
                         'K8S_NAMESPACE')
        self.assertEqual(response.spec.template.spec.containers[0].env[2].value,
                         None)
        self.assertEqual(response.spec.template.spec.containers[0].env[3].name,
                         'CI_VERSION')
        self.assertEqual(response.spec.template.spec.containers[0].env[3].value,
                         'k8s/1.1.1')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[0].name,
                         'cwagentconfig')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[0].mount_path,
                         '/etc/cwagentconfig')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].name,
                         'rootfs')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].mount_path,
                         '/rootfs')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[1].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].name,
                         'dockersock')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].mount_path,
                         '/var/run/docker.sock')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[2].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].name,
                         'varlibdocker')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].mount_path,
                         '/var/lib/docker')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[3].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].name,
                         'sys')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].mount_path,
                         '/sys')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[4].read_only,
                         'true')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[5].name,
                         'devdisk')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[5].mount_path,
                         '/dev/disk')
        self.assertEqual(response.spec.template.spec.containers[0].volume_mounts[5].read_only,
                         'true')

    def test_configmap(self):
        response = self.cloudwatch_agent._configmap()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ConfigMap')
        data = dict({
                'cwagentconfig.json': json.dumps(
                    dict({
                        'agent': {
                            'region': f'{self.region}'
                        },
                        'logs': {
                            'metrics_collected': {
                                'kubernetes': {
                                    'cluster_name': f'{self.cluster_id}',
                                    'metrics_collection_interval': 60
                                }
                            },
                            'force_flush_interval': 5
                        }
                    })
                )
            })
        self.assertEqual(response.data, data)

    def test_service_account(self):
        annotations = dict({'eks.amazonaws.com/role-arn': self.role_arn})
        response = self.cloudwatch_agent._service_account()
        self.assertEqual(response.api_version, 'v1')
        self.assertEqual(response.kind, 'ServiceAccount')

    def test_cluster_role(self):
        response = self.cloudwatch_agent._cluster_role()
        self.assertEqual(response.api_version, 'rbac.authorization.k8s.io/v1')
        self.assertEqual(response.kind, 'ClusterRole')
        self.assertTrue(response.metadata)
        self.assertTrue(response.rules)

    def test_cluster_role_binding(self):
        response = self.cloudwatch_agent._cluster_role_binding()
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
