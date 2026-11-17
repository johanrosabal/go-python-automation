import io
import logging
import os
import threading

# Global variable to store the shared file handler to avoid overwriting and duplicates
_shared_file_handler = None
_log_lock = threading.Lock()
_log_context = threading.local()


class _ThreadContextFilter(logging.Filter):
    """
    Injects thread/worker and active test ID context into every log record,
    and appends formatted records into the current thread's isolated test buffer if active.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        worker = os.getenv("PYTEST_XDIST_WORKER")
        thread_name = threading.current_thread().name
        exec_unit = worker if worker else thread_name
        test_id = getattr(_log_context, "test_id", None)
        record.exec_context = f"[{exec_unit}|{test_id}]" if test_id else f"[{exec_unit}]"
        return True


class _ThreadBufferHandler(logging.Handler):
    """
    Writes log records only into the active thread's StringIO buffer so each
    parallel thread/test gets a 100% sequential, non-interleaved log transcript.
    """
    def emit(self, record: logging.LogRecord):
        buf: io.StringIO = getattr(_log_context, "buffer", None)
        if buf is not None:
            try:
                buf.write(self.format(record) + "\n")
            except Exception:
                pass


_context_filter = _ThreadContextFilter()
_thread_buffer_handler = None


def set_log_context(test_id: str = None):
    """Sets the active test ID for the current thread's log records."""
    _log_context.test_id = test_id


def start_thread_log_capture(test_id: str = None):
    """Starts an isolated in-memory log buffer for the current thread/test."""
    _log_context.test_id = test_id
    _log_context.buffer = io.StringIO()


def stop_thread_log_capture() -> str:
    """Stops the current thread's log capture and returns its sequential log output."""
    buf: io.StringIO = getattr(_log_context, "buffer", None)
    content = buf.getvalue() if buf is not None else ""
    _log_context.buffer = None
    _log_context.test_id = None
    return content


def setup_logger(name):
    """
    Configures and returns a logger instance mimicking Log4j behavior.
    Uses a shared file handler to ensure all logs go to the same file without 
    overwriting each other during the same execution, plus thread-context tagging.
    """
    global _shared_file_handler, _thread_buffer_handler

    logger = logging.getLogger(name)

    # If the logger already has handlers, don't add more
    if logger.handlers:
        return logger

    with _log_lock:
        if logger.handlers:
            return logger

        logger.setLevel(logging.DEBUG)
        logger.addFilter(_context_filter)

        # Create 'logs' directory safely across parallel workers/threads
        os.makedirs('logs', exist_ok=True)

        # Define log format including thread/worker and test ID context
        log_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(exec_context)s %(name)s - %(message)s'
        )

        # Configure Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.addFilter(_context_filter)
        logger.addHandler(console_handler)

        # Configure Shared File Handler (per xdist worker if running in parallel processes)
        if _shared_file_handler is None:
            worker = os.getenv("PYTEST_XDIST_WORKER")
            file_name = f"logs/automation_{worker}.log" if worker else "logs/automation.log"
            _shared_file_handler = logging.FileHandler(file_name, mode='a', encoding='utf-8')
            _shared_file_handler.setFormatter(log_format)
            _shared_file_handler.addFilter(_context_filter)

        if _thread_buffer_handler is None:
            _thread_buffer_handler = _ThreadBufferHandler()
            _thread_buffer_handler.setFormatter(log_format)
            _thread_buffer_handler.addFilter(_context_filter)

        logger.addHandler(_shared_file_handler)
        logger.addHandler(_thread_buffer_handler)

    return logger
