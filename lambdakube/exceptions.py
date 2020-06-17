class LambdaKubeError(Exception):
    """ Base class for all LambdaKubeErrors."""


class EKSError(Exception):
    """ Base class for all EKSErrors."""


class EKSClusterError(EKSError):
    """ Raised when a cluster is not in the correct state."""
