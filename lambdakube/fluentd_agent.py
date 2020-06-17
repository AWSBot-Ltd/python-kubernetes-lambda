from lambdakube.lambda_kube import metadata
import kubernetes.client as client
import kubernetes.client.rest
import os

IMAGE = 'fluent/fluentd-kubernetes-daemonset:v1.7.3-debian-cloudwatch-1.0'
CONFIG_HASH = '8915de4cf9c3551a8dc74c0137a3e83569d28c71044b0359c2578d2e0461825'


class FluentdAgent(object):
    def __init__(self,
                 name='fluentd',
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
        self.cluster_role_binding_name = f'{self.name}-role-binding'
        self.cluster_role_name = f'{self.name}-role'
        self.config_map_name = f'{self.name}-config'

    @property
    def apps_v1_api(self):
        return client.AppsV1Api(self.configuration)

    @property
    def core_v1_api(self):
        return client.CoreV1Api(self.configuration)

    @property
    def rbac_v1_api(self):
        return client.RbacAuthorizationV1Api(self.configuration)

    @property
    def labels(self):
        return dict({'k8s-app': 'fluentd-cloudwatch'})

    @property
    def file_path(self):
        return os.path.dirname(__file__)

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
                    metadata=metadata(
                        labels=self.labels,
                        annotations=dict(
                            {'configHash': CONFIG_HASH})
                    ),
                    spec=client.V1PodSpec(
                        service_account_name=self.name,
                        termination_grace_period_seconds=30,
                        init_containers=[
                            client.V1Container(
                                name='copy-fluentd-config',
                                image='busybox',
                                command=[
                                    'sh',
                                    '-c',
                                    'cp /config-volume/..data/* /fluentd/etc'
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name='config-volume',
                                        mount_path='/config-volume',
                                    ),
                                    client.V1VolumeMount(
                                        name='fluentdconf',
                                        mount_path='/fluentd/etc',
                                    ),
                                ],
                            ),
                            client.V1Container(
                                name='update-log-driver',
                                image='busybox',
                                command=['sh', '-c', '']
                            )
                        ],
                        containers=[
                            client.V1Container(
                                name=self.name,
                                image=self.image,
                                resources=client.V1ResourceRequirements(
                                    limits=dict({
                                        'memory': '400Mi',
                                    }),
                                    requests=dict({
                                        'cpu': '100m',
                                        'memory': '200Mi',
                                    })
                                ),
                                env=[
                                    client.V1EnvVar(
                                        name='REGION',
                                        value=self.region
                                    ),
                                    client.V1EnvVar(
                                        name='CLUSTER_NAME',
                                        value=self.cluster_name
                                    ),
                                    client.V1EnvVar(
                                        name='CI_VERSION',
                                        value='k8s/1.1.1',
                                    ),
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name='config-volume',
                                        mount_path='/config-volume',
                                    ),
                                    client.V1VolumeMount(
                                        name='fluentdconf',
                                        mount_path='/fluentd/etc',
                                    ),
                                    client.V1VolumeMount(
                                        name='varlibdockercontainers',
                                        mount_path='/var/lib/docker/containers',
                                        read_only=True,
                                    ),
                                    client.V1VolumeMount(
                                        name='runlogjournal',
                                        mount_path='/run/log/journal',
                                        read_only=True,
                                    ),
                                    client.V1VolumeMount(
                                        name='dmesg',
                                        mount_path='/var/log/dmesg',
                                        read_only=True,
                                    ),
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name='config-volume',
                                config_map='fluentd-config',
                            ),
                            client.V1Volume(
                                name='fluentdconf',
                                empty_dir={},
                            ),
                            client.V1Volume(
                                name='varlog',
                                host_path='/var/log',
                            ),
                            client.V1Volume(
                                name='varlibdockercontainers',
                                host_path='/var/lib/docker/containers',
                            ),
                            client.V1Volume(
                                name='runlogjournal',
                                host_path='/run/log/journal',
                            ),
                            client.V1Volume(
                                name='dmesg',
                                host_path='/var/log/dmesg',
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

    def _patch_configmap(self):
        try:
            return self.core_v1_api.patch_namespaced_config_map(
                name=self.config_map_name,
                namespace=self.namespace,
                body=self._configmap(),
                pretty=self.pretty,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_configmap(self):
        try:
            return self.core_v1_api.delete_namespaced_config_map(
                name=self.config_map_name,
                namespace=self.namespace
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _configmap(self):
        return client.V1ConfigMap(
            api_version='v1',
            kind='ConfigMap',
            metadata=metadata(
                name=self.config_map_name,
                namespace=self.namespace,
                labels=self.labels,
            ),
            data=dict({
                'fluent.conf': self._read_file(f'{self.file_path}/fluentd/fluent.conf'),
                'containers.conf': self._read_file(f'{self.file_path}/fluentd/containers.conf'),
                'systemd.conf': self._read_file(f'{self.file_path}/fluentd/systemd.conf'),
                'host.conf': self._read_file(f'{self.file_path}/fluentd/host.conf'),
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
                name=self.cluster_role_name,
                body=self._cluster_role(),
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_cluster_role(self):
        try:
            return self.rbac_v1_api.delete_cluster_role(
                name=self.cluster_role_name,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _cluster_role(self):
        return client.V1ClusterRole(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRole',
            metadata=metadata(
                name=self.cluster_role_name,
            ),
            rules=[
                client.V1beta1PolicyRule(
                    api_groups=[""],
                    resources=[
                        "namespaces",
                        "pods",
                        "pods/logs",
                    ],
                    verbs=["get", "list", "watch"],
                )
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
                name=self.cluster_role_binding_name,
                body=self._cluster_role_binding()
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_cluster_role_binding(self):
        try:
            return self.rbac_v1_api.delete_cluster_role_binding(
                name=self.cluster_role_binding_name,
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _cluster_role_binding(self):
        return client.V1ClusterRoleBinding(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRoleBinding',
            metadata=metadata(
                name=self.cluster_role_binding_name,
            ),
            role_ref=client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='ClusterRole',
                name=self.cluster_role_name,
            ),
            subjects=[
                client.V1Subject(
                    kind='ServiceAccount',
                    name=self.name,
                    namespace=self.namespace
                )
            ]
        )

    def _read_file(self, file_path=None):
        with open(file_path) as f:
            data = f.read()
        return data
