from lambdakube.lambda_kube import metadata
import kubernetes.client as client
import kubernetes.client.rest
import json

IMAGE = 'amazon/cloudwatch-agent:1.245315.0'


class CloudWatchAgent(object):
    def __init__(self,
                 name='cloudwatch-agent',
                 namespace='amazon-cloudwatch',
                 configuration=None,
                 region=None,
                 cluster_name=None,
                 pretty=False,
                 image=IMAGE,
                 ):

        self.name = name
        self.namespace = namespace
        self.configuration = configuration
        self.region = region
        self.cluster_name = cluster_name
        self.pretty = pretty
        self.image = image

    @property
    def apps_v1_api(self):
        return client.AppsV1Api(self.configuration)

    @property
    def core_v1_api(self):
        return client.CoreV1Api(self.configuration)

    @property
    def rbac_v1_api(self):
        return client.RbacAuthorizationV1beta1Api(self.configuration)

    @property
    def labels(self):
        return dict({'name': self.name})

    def create(self):
        return [
            self._create_namespace(),
            self._create_daemonset(),
            self._create_configmap(),
            self._create_service_account(),
            self._create_cluster_role(),
            self._create_cluster_role_binding(),
        ]

    def patch(self):
        return [
            self._patch_namespace(),
            self._patch_daemonset(),
            self._patch_configmap(),
            self._patch_service_account(),
            self._patch_cluster_role(),
            self._patch_cluster_role_binding(),
        ]

    def delete(self):
        return [
            self._delete_namespace(),
            self._delete_daemonset(),
            self._delete_configmap(),
            self._delete_service_account(),
            self._delete_cluster_role(),
            self._delete_cluster_role_binding(),
        ]

    def _create_namespace(self):
        try:
            return self.core_v1_api.create_namespace(
                body=self._namespace(),
                pretty=self.pretty,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_namespace(self):
        try:
            return self.core_v1_api.patch_namespace(
                name=self.namespace,
                body=self._namespace(),
                pretty=self.pretty,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_namespace(self):
        try:
            return self.core_v1_api.delete_namespace(
                name=self.namespace,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _namespace(self):
        return client.V1Namespace(
                api_version='v1',
                kind='Namespace',
                metadata=metadata(
                    name=self.namespace,
                    labels=dict({'name': self.namespace}),
                )
            )

    def _create_daemonset(self):
        try:
            return self.apps_v1_api.create_namespaced_daemon_set(
                namespace=self.namespace,
                body=self._daemon_set()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_daemonset(self):
        try:
            return self.apps_v1_api.patch_namespaced_daemon_set(
                name=self.name,
                namespace=self.namespace,
                body=self._daemon_set()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_daemonset(self):
        try:
            return self.apps_v1_api.patch_namespaced_daemon_set(
                name=self.name,
                namespace=self.namespace,
                body=self._daemon_set()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _daemon_set(self):
        return client.V1DaemonSet(
            api_version='apps/v1',
            kind='DaemonSet',
            metadata=metadata(
                name=self.name,
                namespace=self.namespace,
            ),
            spec=client.V1DaemonSetSpec(
                selector=client.V1LabelSelector(
                    match_labels=self.labels
                ),
                template=client.V1PodTemplateSpec(
                    metadata=metadata(name=self.name),
                    spec=client.V1PodSpec(
                        service_account_name=self.name,
                        termination_grace_period_seconds=60,
                        containers=[
                            client.V1Container(
                                name=self.name,
                                image=self.image,
                                resources=client.V1ResourceRequirements(
                                    limits=dict({
                                        'cpu': '200m',
                                        'memory': '200Mi',
                                    }),
                                    requests=dict({
                                        'cpu': '200m',
                                        'memory': '200Mi',
                                    })
                                ),
                                env=[
                                    client.V1EnvVar(
                                        name='HOST_IP',
                                        value_from=client.V1EnvVarSource(
                                            field_ref=client.V1ObjectFieldSelector(
                                                field_path='status.hostIP',
                                            )
                                        ),
                                    ),
                                    client.V1EnvVar(
                                        name='HOST_NAME',
                                        value_from=client.V1EnvVarSource(
                                            field_ref=client.V1ObjectFieldSelector(
                                                field_path='spec.nodeName',
                                            )
                                        ),
                                    ),
                                    client.V1EnvVar(
                                        name='K8S_NAMESPACE',
                                        value_from=client.V1EnvVarSource(
                                            field_ref=client.V1ObjectFieldSelector(
                                                field_path='metadata.namespace',
                                            )
                                        ),
                                    ),
                                    client.V1EnvVar(
                                        name='CI_VERSION',
                                        value='k8s/1.1.1',
                                    ),
                                   ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name='cwagentconfig',
                                        mount_path='/etc/cwagentconfig',
                                    ),
                                    client.V1VolumeMount(
                                        name='rootfs',
                                        mount_path='/rootfs',
                                        read_only='true',
                                    ),
                                    client.V1VolumeMount(
                                        name='dockersock',
                                        mount_path='/var/run/docker.sock',
                                        read_only='true',
                                    ),
                                    client.V1VolumeMount(
                                        name='varlibdocker',
                                        mount_path='/var/lib/docker',
                                        read_only='true',
                                    ),
                                    client.V1VolumeMount(
                                        name='sys',
                                        mount_path='/sys',
                                        read_only='true',
                                    ),
                                    client.V1VolumeMount(
                                        name='devdisk',
                                        mount_path='/dev/disk',
                                        read_only='true',
                                    ),
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name='cwagentconfig',
                                config_map='cwagentconfig',
                            ),
                            client.V1Volume(
                                name='rootfs',
                                host_path='/',
                            ),
                            client.V1Volume(
                                name='dockersock',
                                host_path='/var/run/docker.sock',
                            ),
                            client.V1Volume(
                                name='varlibdocker',
                                host_path='/var/lib/docker',
                            ),
                            client.V1Volume(
                                name='sys',
                                host_path='/sys',
                            ),
                            client.V1Volume(
                                name='devdisk',
                                host_path='/dev/disk/',
                            ),
                        ]
                    )
                )
            )
        )

    def _create_configmap(self):
        try:
            return self.core_v1_api.create_namespaced_config_map(
                namespace=self.namespace,
                body=self._configmap(),
                pretty=self.pretty,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_configmap(self, name='cwagentconfig'):
        try:
            return self.core_v1_api.patch_namespaced_config_map(
                name=name,
                namespace=self.namespace,
                body=self._configmap(),
                pretty=self.pretty,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_configmap(self, name='cwagentconfig'):
        try:
            return self.core_v1_api.delete_namespaced_config_map(
                name=name,
                namespace=self.namespace
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _configmap(self):
        return client.V1ConfigMap(
            api_version='v1',
            kind='ConfigMap',
            metadata=metadata(
                name='cwagentconfig',
                namespace=self.namespace
            ),
            data=dict({
                'cwagentconfig.json': json.dumps(
                    dict({
                        'agent': {
                            'region': f'{self.region}'
                        },
                        'logs': {
                            'metrics_collected': {
                                'kubernetes': {
                                    'cluster_name': f'{self.cluster_name}',
                                    'metrics_collection_interval': 60
                                }
                            },
                            'force_flush_interval': 5
                        }
                    })
                )
            })
        )

    def _create_service_account(self):
        try:
            return self.core_v1_api.create_namespaced_service_account(
                namespace=self.namespace,
                body=self._service_account(),
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_service_account(self):
        try:
            return self.core_v1_api.patch_namespaced_service_account(
                name=self.name,
                namespace=self.namespace,
                body=self._service_account(),
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_service_account(self):
        try:
            return self.core_v1_api.delete_namespaced_service_account(
                name=self.name,
                namespace=self.namespace
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _service_account(self):
        return client.V1ServiceAccount(
            api_version='v1',
            kind='ServiceAccount',
            metadata=metadata(
                name=self.name,
                namespace=self.namespace,
            )
        )

    def _create_cluster_role(self):
        try:
            return self.rbac_v1_api.create_cluster_role(
                body=self._cluster_role()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_cluster_role(self):
        try:
            return self.rbac_v1_api.patch_cluster_role(
                name=f'{self.name}-role',
                body=self._cluster_role(),
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_cluster_role(self):
        try:
            return self.rbac_v1_api.delete_cluster_role(
                name=self.name
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _cluster_role(self):
        return client.V1ClusterRole(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRole',
            metadata=metadata(
                name=f'{self.name}-role',
            ),
            rules=[
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=[
                        "pods",
                        "nodes",
                        "endpoints",
                    ],
                    verbs=["list", "watch"],
                ),
                client.V1PolicyRule(
                    api_groups=["apps"],
                    resources=["replicasets"],
                    verbs=["list", "watch"],
                ),
                client.V1PolicyRule(
                    api_groups=["batch"],
                    resources=["jobs"],
                    verbs=["list", "watch"],
                ),
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["nodes/proxy"],
                    verbs=["get"],
                ),
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["nodes/stats", "configmaps", "events"],
                    verbs=["create"],
                ),
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["configmaps"],
                    resource_names=["cwagent-clusterleader"],
                    verbs=["get", "update"],
                ),
            ]
        )

    def _create_cluster_role_binding(self):
        try:
            return self.rbac_v1_api.create_cluster_role_binding(
                body=self._cluster_role_binding()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_cluster_role_binding(self):
        try:
            return self.rbac_v1_api.patch_cluster_role_binding(
                name=f'{self.name}-role-binding',
                body=self._cluster_role_binding()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_cluster_role_binding(self):
        try:
            return self.rbac_v1_api.delete_cluster_role_binding(
                name=self.name,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _cluster_role_binding(self):
        return client.V1ClusterRoleBinding(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRoleBinding',
            metadata=metadata(
                name=f'{self.name}-role-binding',
            ),
            role_ref=client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='ClusterRole',
                name=f'{self.name}-role',
            ),
            subjects=[
                client.V1Subject(
                    kind='ServiceAccount',
                    name=self.name,
                    namespace=self.namespace
                )
            ]
        )
