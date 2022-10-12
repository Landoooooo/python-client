"""SDK Telemetry helpers."""
from bisect import bisect_left
import threading
import os
from webbrowser import Opera

from splitio.engine.impressions import ImpressionsMode

BUCKETS = (
    1000, 1500, 2250, 3375, 5063,
    7594, 11391, 17086, 25629, 38443,
    57665, 86498, 129746, 194620, 291929,
    437894, 656841, 985261, 1477892, 2216838,
    3325257, 4987885, 7481828
)

MAX_LATENCY = 7481828
MAX_LATENCY_BUCKET_COUNT = 23
MAX_STREAMING_EVENTS = 20

HTTPS_PROXY_ENV = 'HTTPS_PROXY'
IMPRESSIONS_QUEUED = 'impressionsQueued'
IMPRESSIONS_DEDUPED = 'impressionsDeduped'
IMPRESSIONS_DROPPED = 'impressionsDropped'
EVENTS_QUEUED = 'eventsQueued'
EVENTS_DROPPED = 'eventsDropped'
SDK_URL = 'sdk_url'
EVENTS_URL = 'events_url'
AUTH_URL = 'auth_url'
STREAMING_URL = 'streaming_url'
TELEMETRY_URL = 'telemetry_url'
SPLITS_REFRESH_RATE = 'featuresRefreshRate'
SEGMENTS_REFRESH_RATE = 'segmentsRefreshRate'
IMPRESSIONS_REFRESH_RATE = 'impressionsRefreshRate'
EVENTS_REFRESH_RATE = 'eventsPushRate'
TELEMETRY_REFRESH_RATE = 'metrcsRefreshRate'
OPERATION_MODE = 'operationMode'
STORAGE_TYPE = 'storageType'
STREAMING_ENABLED = 'streamingEnabled'
IMPRESSIONS_QUEUE_SIZE = 'impressionsQueueSize'
EVENTS_QUEUE_SIZE = 'eventsQueueSize'
IMPRESSIONS_MODE = 'impressionsMode'
IMPRESSIONS_LISTENER = 'impressionListener'
ACTIVE_FACTORY_COUNT = 'activeFactoryCount'
REDUNDANT_FACTORY_COUNT = 'redundantFactoryCount'
BLOCK_UNTIL_READY_TIMEOUT = 'blockUntilReadyTimeout'
NOT_READY = 'notReady'
TIME_UNTIL_READY = 'timeUntilReady'
REFRESH_RATE = 'refreshRate'
URL_OVERRIDE = 'urlOverride'
HTTP_PROXY = 'httpProxy'

HTTP_LATENCIES = 'httpLatencies'
METHOD_LATENCIES = 'methodLatencies'
METHOD_EXCEPTIONS = 'methodExceptions'
LAST_SYNCHRONIZATIONS = 'lastSynchronizations'
HTTP_ERRORS = 'httpErrors'
STREAMING_EVENTS = 'streamingEvents'
SPLIT = 'split'
SEGMENT = 'segment'
IMPRESSION = 'impression'
IMPRESSION_COUNT = 'impressionCount'
EVENT = 'event'
TELEMETRY = 'telemetry'
TOKEN = 'token'
TREATMENT = 'treatment'
TREATMENTS = 'treatments'
TREATMENT_WITH_CONFIG = 'treatmentWithConfig'
TREATMENTS_WITH_CONFIG = 'treatmentsWithConfig'
TRACK = 'track'

class StorageType(object):
    """
    Storage types constants

    """
    MEMEORY = 'memory'
    REDIS = 'redis'
    LOCALHOST = 'localhost'

class OperationMode(object):
    """
    Storage modes constants

    """
    MEMEORY = 'in-memory'
    REDIS = 'redis-consumer'

def get_latency_bucket_index(micros):
    """
    Find the bucket index for a measured latency.

    :param micros: Measured latency in microseconds
    :type micros: int
    :return: Bucket index for the given latency
    :rtype: int
    """
    if micros > MAX_LATENCY:
        return len(BUCKETS) - 1

    return bisect_left(BUCKETS, micros)

class MethodLatencies(object):
    """
    Method Latency class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._treatment = [0] * 23
            self._treatments = [0] * 23
            self._treatment_with_config = [0] * 23
            self._treatments_with_config = [0] * 23
            self._track = [0] * 23

    def add_latency(self, method, latency):
        """
        Add Latency method

        :param method: passed method name
        :type method: str
        :param latency: amount of latency in microseconds
        :type latency: int
        """
        latency_bucket = get_latency_bucket_index(latency)
        with self._lock:
            if method == TREATMENT:
                self._treatment[latency_bucket] = self._treatment[latency_bucket] + 1
            elif method == TREATMENTS:
                self._treatments[latency_bucket] = self._treatments[latency_bucket] + 1
            elif method == TREATMENT_WITH_CONFIG:
                self._treatment_with_config[latency_bucket] = self._treatment_with_config[latency_bucket] + 1
            elif method == TREATMENTS_WITH_CONFIG:
                self._treatments_with_config[latency_bucket] = self._treatments_with_config[latency_bucket] + 1
            elif method == TRACK:
                self._track[latency_bucket] = self._track[latency_bucket] + 1
            else:
                return

    def pop_all(self):
        """
        Pop all latencies

        :return: Dictonary of latencies
        :rtype: dict
        """
        with self._lock:
            latencies = {METHOD_LATENCIES: {TREATMENT: self._treatment, TREATMENTS: self._treatments,
                            TREATMENT_WITH_CONFIG: self._treatment_with_config, TREATMENTS_WITH_CONFIG: self._treatments_with_config,
                            TRACK: self._track}
                }
            self._reset_all()
            return latencies

class HTTPLatencies(object):
    """
    HTTP Latency class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._split = [0] * 23
            self._segment = [0] * 23
            self._impression = [0] * 23
            self._impression_count = [0] * 23
            self._event = [0] * 23
            self._telemetry = [0] * 23
            self._token = [0] * 23

    def add_latency(self, resource, latency):
        """
        Add Latency method

        :param resource: passed resource name
        :type resource: str
        :param latency: amount of latency in microseconds
        :type latency: int
        """
        latency_bucket = get_latency_bucket_index(latency)
        with self._lock:
            if resource == SPLIT:
                self._split[latency_bucket] = self._split[latency_bucket] + 1
            elif resource == SEGMENT:
                self._segment[latency_bucket] = self._segment[latency_bucket] + 1
            elif resource == IMPRESSION:
                self._impression[latency_bucket] = self._impression[latency_bucket] + 1
            elif resource == IMPRESSION_COUNT:
                self._impression_count[latency_bucket] = self._impression_count[latency_bucket] + 1
            elif resource == EVENT:
                self._event[latency_bucket] = self._event[latency_bucket] + 1
            elif resource == TELEMETRY:
                self._telemetry[latency_bucket] = self._telemetry[latency_bucket] + 1
            elif resource == TOKEN:
                self._token[latency_bucket] = self._token[latency_bucket] + 1
            else:
                return

    def pop_all(self):
        """
        Pop all latencies

        :return: Dictonary of latencies
        :rtype: dict
        """
        with self._lock:
            latencies = {HTTP_LATENCIES: {SPLIT: self._split, SEGMENT: self._segment, IMPRESSION: self._impression,
                                        IMPRESSION_COUNT: self._impression_count, EVENT: self._event,
                                        TELEMETRY: self._telemetry, TOKEN: self._token}
                    }
            self._reset_all()
            return latencies

class MethodExceptions(object):
    """
    Method exceptions class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._treatment = 0
            self._treatments = 0
            self._treatment_with_config = 0
            self._treatments_with_config = 0
            self._track = 0

    def add_exception(self, method):
        """
        Add exceptions method

        :param method: passed method name
        :type method: str
        """
        with self._lock:
            if method == TREATMENT:
                self._treatment = self._treatment + 1
            elif method == TREATMENTS:
                self._treatments = self._treatments + 1
            elif method == TREATMENT_WITH_CONFIG:
                self._treatment_with_config = self._treatment_with_config + 1
            elif method == TREATMENTS_WITH_CONFIG:
                self._treatments_with_config = self._treatments_with_config + 1
            elif method == TRACK:
                self._track = self._track + 1
            else:
                return

    def pop_all(self):
        """
        Pop all exceptions

        :return: Dictonary of exceptions
        :rtype: dict
        """
        with self._lock:
            exceptions = {METHOD_EXCEPTIONS: {TREATMENT: self._treatment, TREATMENTS: self._treatments,
                                TREATMENT_WITH_CONFIG: self._treatment_with_config, TREATMENTS_WITH_CONFIG: self._treatments_with_config,
                                TRACK: self._track}
                }
            self._reset_all()
            return exceptions

class LastSynchronization(object):
    """
    Last Synchronization info class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._split = 0
            self._segment = 0
            self._impression = 0
            self._impression_count = 0
            self._event = 0
            self._telemetry = 0
            self._token = 0

    def add_latency(self, resource, latency):
        """
        Add Latency method

        :param resource: passed resource name
        :type resource: str
        :param latency: amount of latency
        :type latency: int
        """
        with self._lock:
            if resource == SPLIT:
                self._split = latency
            elif resource == SEGMENT:
                self._segment = latency
            elif resource == IMPRESSION:
                self._impression = latency
            elif resource == IMPRESSION_COUNT:
                self._impression_count = latency
            elif resource == EVENT:
                self._event = latency
            elif resource == TELEMETRY:
                self._telemetry = latency
            elif resource == TOKEN:
                self._token = latency
            else:
                return

    def get_all(self):
        """
        get all exceptions

        :return: Dictonary of latencies
        :rtype: dict
        """
        with self._lock:
            return {LAST_SYNCHRONIZATIONS: {SPLIT: self._split, SEGMENT: self._segment, IMPRESSION: self._impression,
                                        IMPRESSION_COUNT: self._impression_count, EVENT: self._event,
                                        TELEMETRY: self._telemetry, TOKEN: self._token}
                    }

class HTTPErrors(object):
    """
    Last Synchronization info class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._split = {}
            self._segment = {}
            self._impression = {}
            self._impression_count = {}
            self._event = {}
            self._telemetry = {}
            self._token = {}

    def add_error(self, resource, status):
        """
        Add Latency method

        :param resource: passed resource name
        :type resource: str
        :param status: http error code
        :type status: str
        """
        with self._lock:
            if resource == SPLIT:
                if status not in self._split:
                    self._split[status] = 0
                self._split[status] = self._split[status] + 1
            elif resource == SEGMENT:
                if status not in self._segment:
                    self._segment[status] = 0
                self._segment[status] = self._segment[status] + 1
            elif resource == IMPRESSION:
                if status not in self._impression:
                    self._impression[status] = 0
                self._impression[status] = self._impression[status] + 1
            elif resource == IMPRESSION_COUNT:
                if status not in self._impression_count:
                    self._impression_count[status] = 0
                self._impression_count[status] = self._impression_count[status] + 1
            elif resource == EVENT:
                if status not in self._event:
                    self._event[status] = 0
                self._event[status] = self._event[status] + 1
            elif resource == TELEMETRY:
                if status not in self._telemetry:
                    self._telemetry[status] = 0
                self._telemetry[status] = self._telemetry[status] + 1
            elif resource == TOKEN:
                if status not in self._token:
                    self._token[status] = 0
                self._token[status] = self._token[status] + 1
            else:
                return

    def pop_all(self):
        """
        Pop all errors

        :return: Dictonary of exceptions
        :rtype: dict
        """
        with self._lock:
            http_errors = {HTTP_ERRORS: {SPLIT: self._split, SEGMENT: self._segment, IMPRESSION: self._impression,
                                        IMPRESSION_COUNT: self._impression_count, EVENT: self._event,
                                        TELEMETRY: self._telemetry, TOKEN: self._token}
                    }
            self._reset_all()
            return http_errors

class TelemetryCounters(object):
    """
    Method exceptions class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._impressions_queued = 0
            self._impressions_deduped = 0
            self._impressions_dropped = 0
            self._events_queued = 0
            self._events_dropped = 0
            self._auth_rejections = 0
            self._token_refreshes = 0
            self._session_length = 0

    def append_value(self, resource, value):
        """
        Append to the resource value

        :param resource: passed resource name
        :type resource: str
        :param value: value to be appended
        :type value: int
        """
        with self._lock:
            if resource == IMPRESSIONS_QUEUED:
                self._impressions_queued = self._impressions_queued + value
            elif resource == IMPRESSIONS_DEDUPED:
                self._impressions_deduped = self._impressions_deduped + value
            elif resource == IMPRESSIONS_DROPPED:
                self._impressions_dropped = self._impressions_dropped + value
            elif resource == EVENTS_QUEUED:
                self._events_queued = self._events_queued + value
            elif resource == EVENTS_DROPPED:
                self._events_dropped = self._events_dropped + value
            else:
                return

    def append_auth_rejections(self):
        """
        Increament the auth rejection resource by one.

        """
        with self._lock:
            self._auth_rejections = self._auth_rejections + 1

    def append_token_refreshes(self):
        """
        Increament the token refreshes resource by one.

        """
        with self._lock:
            self._token_refreshes = self._token_refreshes + 1

    def set_value(self, resource, value):
        """
        Set the resource value

        :param resource: passed resource name
        :type resource: str
        :param value: value to be set
        :type value: int
        """
        with self._lock:
            if resource == IMPRESSIONS_QUEUED:
                self._impressions_queued = value
            elif resource == IMPRESSIONS_DEDUPED:
                self._impressions_deduped = value
            elif resource == IMPRESSIONS_DROPPED:
                self._impressions_dropped = value
            elif resource == EVENTS_QUEUED:
                self._events_queued = value
            elif resource == EVENTS_DROPPED:
                self._events_dropped = value
            else:
                return

    def set_session_length(self, session):
        """
        Set the session length value

        :param session: value to be set
        :type session: int
        """
        with self._lock:
            self._session_length = session

    def get_counter_stats(self, resource):
        """
        Get resource counter value

        :param resource: passed resource name
        :type resource: str

        :return: resource value
        :rtype: int
        """

        with self._lock:
            if resource == IMPRESSIONS_QUEUED:
                return self._impressions_queued
            elif resource == IMPRESSIONS_DEDUPED:
                return self._impressions_deduped
            elif resource == IMPRESSIONS_DROPPED:
                return self._impressions_dropped
            elif resource == EVENTS_QUEUED:
                return self._events_queued
            elif resource == EVENTS_DROPPED:
                return self._events_dropped
            else:
                return 0

    def get_session_length(self):
        """
        Get session length

        :return: session length value
        :rtype: int
        """
        with self._lock:
            return self._session_length

    def pop_auth_rejections(self):
        """
        Pop auth rejections

        :return: auth rejections value
        :rtype: int
        """
        with self._lock:
            auth_rejections = self._auth_rejections
            self._auth_rejections = 0
            return auth_rejections

    def pop_token_refreshes(self):
        """
        Pop token refreshes

        :return: token refreshes value
        :rtype: int
        """
        with self._lock:
            token_refreshes = self._token_refreshes
            self._token_refreshes = 0
            return token_refreshes

class StreamingEvent(object):
    """
    Streaming event class

    """
    def __init__(self, streaming_event):
        """
        Constructor

        :param streaming_event: Streaming event dict:
                {'type': string, 'data': string, 'time': string}
        :type streaming_event: dict
        """
        self._lock = threading.RLock()
        self._type = streaming_event['type']
        self._data = streaming_event['data']
        self._time = streaming_event['time']

    @property
    def type(self):
        """
        Get streaming event type

        :return: streaming event type
        :rtype: str
        """
        with self._lock:
            return self._type

    @property
    def data(self):
        """
        Get streaming event data

        :return: streaming event data
        :rtype: str
        """
        with self._lock:
            return self._data

    @property
    def time(self):
        """
        Get streaming event time

        :return: streaming event time
        :rtype: int
        """
        with self._lock:
            return self._time

class StreamingEvents(object):
    """
    Streaming events class

    """

    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        with self._lock:
            self._streaming_events = []

    def record_streaming_event(self, streaming_event):
        """
        Record new streaming event

        :param streaming_event: Streaming event dict:
                {'type': string, 'data': string, 'time': string}
        :type streaming_event: dict
        """
        with self._lock:
            if len(self._streaming_events) < MAX_STREAMING_EVENTS:
                self._streaming_events.append(StreamingEvent(streaming_event))

    def pop_streaming_events(self):
        """
        Get and reset streaming events

        :return: streaming events dict
        :rtype: dict
        """

        with self._lock:
            streaming_events = self._streaming_events
            self._streaming_events = []
            return {STREAMING_EVENTS: [{'e': streaming_event.type, 'd': streaming_event.data,
                                         't': streaming_event.time} for streaming_event in streaming_events]}
class RefreshRates(object):
    """
    Refresh rates class

    """
    def __init__(self, splits=0, segments=0, impressions=0, events=0, telemetry=0):
        """
        Constructor

        :param splits: splits refresh rate
        :type splits: int
        :param segments: segments refresh rate
        :type segments: int
        :param impressions: impressions refresh rate
        :type impressions: int
        :param events: events refresh rate
        :type events: int
        :param telemetry: telemetry refresh rate
        :type telemetry: int
        """
        self._lock = threading.RLock()
        self._splits = splits
        self._segments = segments
        self._impressions = impressions
        self._events = events
        self._telemetry = telemetry

    @property
    def splits(self):
        """
        Get splits refresh rate

        :return: splits refresh rate
        :rtype: int
        """
        with self._lock:
            return self._splits

    @property
    def segments(self):
        """
        Get segments refresh rate

        :return: segments refresh rate
        :rtype: int
        """
        with self._lock:
            return self._segments

    @property
    def impressions(self):
        """
        Get impressions refresh rate

        :return: impressions refresh rate
        :rtype: int
        """
        with self._lock:
            return self._impressions

    @property
    def events(self):
        """
        Get events refresh rate

        :return: events refresh rate
        :rtype: int
        """
        with self._lock:
            return self._events

    @property
    def telemetry(self):
        """
        Get telemetry refresh rate

        :return: telemetry refresh rate
        :rtype: int
        """
        with self._lock:
            return self._telemetry

class URLOverrides(object):
    """
    URL overrides class

    """
    def __init__(self, sdk=False, events=False, auth=False, streaming=False, telemetry=False):
        """
        Constructor

        :param sdk: sdk URL flag
        :type splits: boolean
        :param events: events URL flag
        :type events: boolean
        :param auth: auth URL flag
        :type auth: boolean
        :param streaming: streaming URL flag
        :type streaming: boolean
        :param telemetry: telemetry URL flag
        :type telemetry: boolean
        """
        self._lock = threading.RLock()
        self._sdk =  sdk
        self._events = events
        self._auth = auth
        self._streaming = streaming
        self._telemetry = telemetry

    @property
    def sdk(self):
        """
        Get sdk url flag

        :return: sdk url flag
        :rtype: boolean
        """
        with self._lock:
            return self._sdk

    @property
    def events(self):
        """
        Get events url flag

        :return: events url flag
        :rtype: boolean
        """
        with self._lock:
            return self._events

    @property
    def auth(self):
        """
        Get auth url flag

        :return: auth url flag
        :rtype: boolean
        """
        with self._lock:
            return self._auth

    @property
    def streaming(self):
        """
        Get streaming url flag

        :return: streaming url flag
        :rtype: boolean
        """
        with self._lock:
            return self._streaming

    @property
    def telemetry(self):
        """
        Get telemetry url flag

        :return: telemetry url flag
        :rtype: boolean
        """
        with self._lock:
            return self._telemetry

class TelemetryConfig(object):
    """
    Telemetry init config class

    """
    def __init__(self):
        """Constructor"""
        self._lock = threading.RLock()
        self._reset_all()

    def _reset_all(self):
        """Reset variables"""
        with self._lock:
            self._block_until_ready_timeout = 0
            self._not_ready = 0
            self._time_until_ready = 0
            self._operation_mode = None
            self._storage_type = None
            self._streaming_enabled = None
            self._refresh_rate = RefreshRates()
            self._url_override = URLOverrides()
            self._impressions_queue_size = 0
            self._events_queue_size = 0
            self._impressions_mode = None
            self._impression_listener = False
            self._http_proxy = None
            self._active_factory_count = 0
            self._redundant_factory_count = 0

    def record_config(self, config):
        """
        Record configurations.

        :param config: config dict: {
            'operationMode': string, 'storageType': string, 'streamingEnabled': boolean,
            'refreshRate' : {
                'featuresRefreshRate': int,
                'segmentsRefreshRate': int,
                'impressionsRefreshRate': int,
                'eventsPushRate': int,
                'metrcsRefreshRate': int
            }
            'urlOverride' : {
                'sdk_url': boolean, 'events_url': boolean, 'auth_url': boolean,
                'streaming_url': boolean, 'telemetry_url': boolean, }
            },
            'impressionsQueueSize': int, 'eventsQueueSize': int, 'impressionsMode': string,
            'impressionsListener': boolean, 'activeFactoryCount': int, 'redundantFactoryCount': int
        }
        :type config: dict
        """

        with self._lock:
            self._operation_mode = self._get_operation_mode(config[OPERATION_MODE])
            self._storage_type = self._get_storage_type(config[OPERATION_MODE])
            self._streaming_enabled = config[STREAMING_ENABLED]
            self._refresh_rate = self._get_refresh_rates(config)
            self._url_override = self._get_url_overrides(config)
            self._impressions_queue_size = config[IMPRESSIONS_QUEUE_SIZE]
            self._events_queue_size = config[EVENTS_QUEUE_SIZE]
            self._impressions_mode = self._get_impressions_mode(config[IMPRESSIONS_MODE])
            self._impression_listener = True if config[IMPRESSIONS_LISTENER] is not None else False
            self._http_proxy = self._check_if_proxy_detected()
            self._active_factory_count = config[ACTIVE_FACTORY_COUNT]
            self._redundant_factory_count = config[REDUNDANT_FACTORY_COUNT]

    def record_ready_time(self, ready_time):
        """
        Record ready time.

        :param ready_time: SDK ready time
        :type ready_time: int
        """
        with self._lock:
            self._time_until_ready = ready_time

    def record_bur_time_out(self):
        """
        Record block until ready timeout count

        """
        with self._lock:
            self._block_until_ready_timeout = self._block_until_ready_timeout + 1

    def record_not_ready_usage(self):
        """
        record non-ready usage count

        """
        with self._lock:
            self._not_ready = self._not_ready + 1

    def get_bur_time_outs(self):
        """
        Get block until ready timeout.

        :return: block until ready timeouts count
        :rtype: int
        """
        with self._lock:
            return self._block_until_ready_timeout

    def get_non_ready_usage(self):
        """
        Get non-ready usage.

        :return: non-ready usage count
        :rtype: int
        """
        with self._lock:
            return self._not_ready

    def get_stats(self):
        """
        Get config stats.

        :return: dict of all config stats.
        :rtype: dict
        """
        with self._lock:
            return {
                BLOCK_UNTIL_READY_TIMEOUT:  self._block_until_ready_timeout,
                NOT_READY: self._not_ready,
                TIME_UNTIL_READY: self._time_until_ready,
                OPERATION_MODE: self._operation_mode,
                STORAGE_TYPE: self._storage_type,
                STREAMING_ENABLED: self._streaming_enabled,
                REFRESH_RATE: {'sp': self._refresh_rate.splits,
                                'se': self._refresh_rate.segments,
                                'im': self._refresh_rate.impressions,
                                'ev': self._refresh_rate.events,
                                'te': self._refresh_rate.telemetry},
                URL_OVERRIDE: {'s': self._url_override.sdk,
                                'e': self._url_override.events,
                                'a': self._url_override.auth,
                                'st': self._url_override.streaming,
                                't': self._url_override.telemetry},
                IMPRESSIONS_QUEUE_SIZE: self._impressions_queue_size,
                EVENTS_QUEUE_SIZE: self._events_queue_size,
                IMPRESSIONS_MODE: self._impressions_mode,
                IMPRESSIONS_LISTENER: self._impression_listener,
                HTTP_PROXY: self._http_proxy,
                ACTIVE_FACTORY_COUNT: self._active_factory_count,
                REDUNDANT_FACTORY_COUNT: self._redundant_factory_count
            }

    def _get_operation_mode(self, op_mode):
        """
        Get formatted operation mode

        :param op_mode: config operation mode
        :type config: str

        :return: operation mode
        :rtype: int
        """
        with self._lock:
            if OperationMode.MEMEORY in op_mode:
                return 0
            elif op_mode == OperationMode.REDIS:
                return 1
            else:
                return 2

    def _get_storage_type(self, op_mode):
        """
        Get storage type from operation mode

        :param op_mode: config operation mode
        :type config: str

        :return: storage type
        :rtype: str
        """
        with self._lock:
            if OperationMode.MEMEORY in op_mode:
                return StorageType.MEMEORY
            elif StorageType.REDIS in op_mode:
                return StorageType.REDIS
            else:
                return StorageType.LOCALHOST

    def _get_refresh_rates(self, config):
        """
        Get refresh rates within config dict

        :param config: config dict
        :type config: dict

        :return: refresh rates
        :rtype: RefreshRates object
        """
        with self._lock:
            return RefreshRates(config[SPLITS_REFRESH_RATE], config[SEGMENTS_REFRESH_RATE],
                config[IMPRESSIONS_REFRESH_RATE], config[EVENTS_REFRESH_RATE], config[TELEMETRY_REFRESH_RATE])

    def _get_url_overrides(self, config):
        """
        Get URL override within the config dict.

        :param config: config dict
        :type config: dict

        :return: URL overrides dict
        :rtype: URLOverrides object
        """
        with self._lock:
            return URLOverrides (
                True if SDK_URL in config else False,
                True if EVENTS_URL in config else False,
                True if AUTH_URL in config else False,
                True if STREAMING_URL in config else False,
                True if TELEMETRY_URL in config else False
            )

    def _get_impressions_mode(self, imp_mode):
        """
        Get impressions mode from operation mode

        :param op_mode: config operation mode
        :type config: str

        :return: impressions mode
        :rtype: int
        """
        with self._lock:
            if imp_mode == ImpressionsMode.DEBUG:
                return 1
            elif imp_mode == ImpressionsMode.OPTIMIZED:
                return 0
            else:
                return 2

    def _check_if_proxy_detected(self):
        """
        Return boolean flag if network https proxy is detected

        :return: https network proxy flag
        :rtype: boolean
        """
        with self._lock:
            for x in os.environ:
                if x.upper() == HTTPS_PROXY_ENV:
                    return True
            return False