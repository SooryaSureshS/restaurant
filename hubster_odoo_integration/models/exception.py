


class ConnectorException(BaseException):
    """ Base Exception for the connectors """


class NoConnectorUnitError(ConnectorException):
    """ No ConnectorUnit has been found """


class InvalidDataError(ConnectorException):
    """ Data Invalid """


class MappingError(ConnectorException):
    """ An error occurred during a mapping transformation. """


class JobError(ConnectorException):
    """ A job had an error """


class NoSuchJobError(JobError):
    """ The job does not exist. """


class NotReadableJobError(JobError):
    """ The job cannot be read from the storage. """


class FailedJobError(JobError):
    """ A job had an error having to be resolved. """


class RetryableJobError(JobError):
    """ A job had an error but can be retried.

    The job will be retried after the given number of seconds.
    If seconds is empty, it will be retried according to the ``retry_pattern``
    of the job or by :const:`connector.queue.job.RETRY_INTERVAL` if nothing
    is defined.

    If ``ignore_retry`` is True, the retry counter will not be increased.
    """

    def __init__(self, msg, seconds=None, ignore_retry=False):
        super(RetryableJobError, self).__init__(msg)
        self.seconds = seconds
        self.ignore_retry = ignore_retry


class NetworkRetryableError(RetryableJobError):
    """ A network error caused the failure of the job, it can be retried later.
    """


class NothingToDoJob(JobError):
    """ The Job has nothing to do. """


class NoExternalId(RetryableJobError):
    """ No External ID found, it can be retried later. """


class IDMissingInBackend(JobError):
    """ The ID does not exist in the backend """


class ManyIDSInBackend(JobError):
    """Unique key exists many times in backend"""


class ChannelNotFound(ConnectorException):
    """ A channel could not be found """



class OrderImportRuleRetry(RetryableJobError):
    """ The sale order import will be retried later. """
    
class CanceledJobError(JobError):
    """ A job is canceled """
