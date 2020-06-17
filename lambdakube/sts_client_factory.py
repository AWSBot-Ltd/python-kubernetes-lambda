CLUSTER_NAME_HEADER = 'x-k8s-aws-id'


class STSClientFactory(object):
    def __init__(self, session):
        self._session = session

    def get_sts_client(self, region_name=None, role_arn=None):
        client_kwargs = {
            'region_name': region_name
        }
        if role_arn is not None:
            creds = self._get_role_credentials(region_name, role_arn)
            client_kwargs['aws_access_key_id'] = creds['AccessKeyId']
            client_kwargs['aws_secret_access_key'] = creds['SecretAccessKey']
            client_kwargs['aws_session_token'] = creds['SessionToken']
        sts = self._session.create_client('sts', **client_kwargs)
        self._register_cluster_name_handlers(sts)
        return sts

    def _get_role_credentials(self, region_name, role_arn):
        sts = self._session.create_client('sts', region_name)
        return sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='EKSGetTokenAuth'
        )['Credentials']

    def _register_cluster_name_handlers(self, sts_client):
        sts_client.meta.events.register(
            'provide-client-params.sts.GetCallerIdentity',
            self._retrieve_cluster_name
        )
        sts_client.meta.events.register(
            'before-sign.sts.GetCallerIdentity',
            self._inject_cluster_name_header
        )

    def _retrieve_cluster_name(self, params, context, **kwargs):
        if 'ClusterName' in params:
            context['eks_cluster'] = params.pop('ClusterName')

    def _inject_cluster_name_header(self, request, **kwargs):
        if 'eks_cluster' in request.context:
            request.headers[
                CLUSTER_NAME_HEADER] = request.context['eks_cluster']
