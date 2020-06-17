from lambdakube.lambda_kube import metadata
import kubernetes.client as client
import kubernetes.client.rest

IMAGE = 'docker.io/amazon/aws-alb-ingress-controller:v1.1.4'


class ALBIngress(object):
    def __init__(self,
                 name='alb-ingress-controller',
                 namespace='kube-system',
                 configuration=None,
                 role_arn=None,
                 cluster_name=None,
                 region=None,
                 vpc_id=None,
                 pretty=False,
                 image=IMAGE,
                 ):

        self.name = name
        self.namespace = namespace
        self.configuration = configuration
        self.role_arn = role_arn
        self.cluster_name = cluster_name
        self.region = region
        self.vpc_id = vpc_id
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
        return dict({'app.kubernetes.io/name': self.name})

    def create(self):
        return [
            self._create_deployment(),
            self._create_service_account(),
            self._create_cluster_role(),
            self._create_cluster_role_binding(),
        ]

    def patch(self):
        return [
            self._patch_deployment(),
            self._patch_service_account(),
            self._patch_cluster_role(),
            self._patch_cluster_role_binding(),
        ]

    def delete(self):
        return [
            self._delete_deployment(),
            self._delete_service_account(),
            self._delete_cluster_role(),
            self._delete_cluster_role_binding(),
        ]

    def _create_deployment(self):
        try:
            return self.apps_v1_api.create_namespaced_deployment(
                body=self._deployment(),
                namespace=self.namespace,
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _patch_deployment(self):
        try:
            return self.apps_v1_api.patch_namespaced_deployment(
                name=self.name,
                body=self._deployment(),
                namespace=self.namespace,
                pretty=self.pretty
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

    def _delete_deployment(self):
        try:
            return self.apps_v1_api.delete_namespaced_deployment(
                name=self.name,
                namespace=self.namespace
            )
        except kubernetes.client.rest.ApiException as e:
            print(e)

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
                name=self.name,
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
                name=self.name,
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

    def _deployment(self):
        return client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=metadata(
                name=self.name,
                namespace=self.namespace,
                labels=self.labels
            ),
            spec=client.V1DeploymentSpec(
                selector=client.V1LabelSelector(
                    match_labels=self.labels
                ),
                template=client.V1PodTemplateSpec(
                    metadata=metadata(
                        labels=self.labels,
                    ),
                    spec=client.V1PodSpec(
                        service_account_name=self.name,
                        containers=[
                            client.V1Container(
                                name=self.name,
                                image=self.image,
                                args=[
                                    '--ingress-class=alb',
                                    f'--cluster-name={self.cluster_name}',
                                    f'--aws-vpc-id={self.vpc_id}',
                                    f'--aws-region={self.region}',
                                ]
                            )
                        ]
                    )
                )
            )
        )

    def _service_account(self):
        return client.V1ServiceAccount(
            api_version='v1',
            kind='ServiceAccount',
            metadata=metadata(
                name=self.name,
                namespace=self.namespace,
                annotations=dict({
                    'eks.amazonaws.com/role-arn': self.role_arn
                }),
                labels=self.labels
            )
        )

    def _cluster_role(self):
        return client.V1ClusterRole(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRole',
            metadata=metadata(
                name=self.name,
                labels=self.labels,
            ),
            rules=[
                client.V1PolicyRule(
                    api_groups=["", "extensions"],
                    resources=[
                        "configmaps",
                        "endpoints",
                        "events",
                        "ingresses",
                        "ingresses/status",
                        "services"
                    ],
                    verbs=[
                        "create",
                        "get",
                        "list",
                        "update",
                        "watch",
                        "patch"
                    ],
                ),
                client.V1PolicyRule(
                    api_groups=["", "extensions"],
                    resources=[
                        "nodes",
                        "pods",
                        "secrets",
                        "services",
                        "namespaces"
                    ],
                    verbs=["get", "list", "watch"]
                ),
            ]
        )

    def _cluster_role_binding(self):
        return client.V1ClusterRoleBinding(
            api_version='rbac.authorization.k8s.io/v1',
            kind='ClusterRoleBinding',
            metadata=metadata(
                name=self.name,
                labels=self.labels,
            ),
            role_ref=client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='ClusterRole',
                name=self.name
            ),
            subjects=[
                client.V1Subject(
                    kind='ServiceAccount',
                    name=self.name,
                    namespace=self.namespace
                )
            ]
        )
