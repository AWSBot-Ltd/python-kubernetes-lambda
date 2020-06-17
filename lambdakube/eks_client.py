

class EKSClient(object):
    def __init__(self, session, cluster_name):
        self._session = session
        self._cluster_name = cluster_name

    def get_cluster_info(self):
        """
        Use an eks describe-cluster call to get the cluster information
        """
        client = self._session.create_client("eks")
        full_description = client.describe_cluster(name=self._cluster_name)

        return full_description
