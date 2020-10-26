"""Synchronization manager module."""
import logging
from threading import Thread
from queue import Queue
from splitio.push.manager import PushManager, Status
from splitio.api import APIException


_LOGGER = logging.getLogger(__name__)


class Manager(object):
    """Manager Class."""

    def __init__(self, ready_flag, synchronizer, auth_api):
        """
        Construct Manager.

        :param ready_flag: Flag to set when splits initial sync is complete.
        :type ready_flag: threading.Event

        :param split_synchronizers: synchronizers for performing start/stop logic
        :type split_synchronizers: splitio.push.synchronizer.Synchronizer

        :param auth_api: Authentication api client
        :type auth_api: splitio.api.auth.AuthAPI
        """
        self._ready_flag = ready_flag
        self._synchronizer = synchronizer
        self._queue = Queue()
        self._push = PushManager(auth_api, synchronizer, self._queue)
        self._push_status_handler = Thread(target=self._streaming_feedback_handler, name='push_status_handler')
        self._push_status_handler.setDaemon(True)

    def start(self):
        """Start the SDK synchronization tasks."""
        # TODO: Use a config option to choose how to start.
        self._start_streaming()

    def stop(self):
        """Stop manager logic."""
        _LOGGER.info('Stopping manager tasks')
        self._push.stop()
        self._synchronizer.stop_periodic_fetching()
        self._synchronizer.stop_periodic_data_recording()

    def _start_streaming(self):
        """Start the sdk synchronization with streaming enabled."""
        try:
            self._synchronizer.sync_all()
            self._ready_flag.set()
            self._synchronizer.start_periodic_data_recording()
            self._push_status_handler.start()
            self._push.start()

        except APIException:
            _LOGGER.error('Exception raised starting Split Manager')
            _LOGGER.debug('Exception information: ', exc_info=True)
            raise
        except RuntimeError:
            _LOGGER.error('Exception raised starting Split Manager')
            _LOGGER.debug('Exception information: ', exc_info=True)
            raise

    def _start_polling(self):
        """Start manager logic."""
        try:
            self._synchronizer.sync_all()
            self._ready_flag.set()
            self._synchronizer.start_periodic_fetching()
            self._synchronizer.start_periodic_data_recording()
        except APIException:
            _LOGGER.error('Exception raised starting Split Manager')
            _LOGGER.debug('Exception information: ', exc_info=True)
            raise
        except RuntimeError:
            _LOGGER.error('Exception raised starting Split Manager')
            _LOGGER.debug('Exception information: ', exc_info=True)
            raise

    def _streaming_feedback_handler(self):
        """
        Handle status updates from the streaming subsystem.

        :param status: current status of the streaming pipeline.
        :type status: splitio.push.status_stracker.Status
        """
        while True:
            status = self._queue.get()
            if status == Status.PUSH_SUBSYSTEM_UP:
                _LOGGER.info('streaming up and running. disabling periodic fetching.')
                self._synchronizer.stop_periodic_fetching()
                self._push.update_workers_status(True)
                self._synchronizer.sync_all()
            elif status == Status.PUSH_SUBSYSTEM_DOWN:
                _LOGGER.info('streaming temporarily down. starting periodic fetching')
                self._push.update_workers_status(False)
                self._synchronizer.start_periodic_fetching()
                # TODO: Disable workers
            elif status == Status.PUSH_RETRYABLE_ERROR:
                _LOGGER.info('error in streaming. restarting flow')
                # TODO: Disable workers
                self._synchronizer.start_periodic_fetching()
                self._push.stop(True)
                self._push.start()
            elif status == Status.PUSH_NONRETRYABLE_ERROR:
                _LOGGER.info('non-recoverable error in streaming. switching to polling.')
                self._synchronizer.start_periodic_fetching()
                self._push.stop(False)
                return
