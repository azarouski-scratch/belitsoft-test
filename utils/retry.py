import time
import functools
import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

LOG = logging.getLogger(__name__)

class RetryException(Exception):
    pass


def _load_retry_defaults():
    """Load retry defaults from environment or config.yaml.

    Precedence: env (RETRY_ATTEMPTS, RETRY_WAIT) > config.yaml > hard-coded.
    """
    load_dotenv()
    # Hard-coded defaults
    defaults = {'attempts': 3, 'wait_seconds': 1}

    # Try config.yaml in project root or utils/ parent
    cfg_paths = [
        Path(__file__).resolve().parent.parent / 'config.yaml',
        Path.cwd() / 'config.yaml',
    ]
    cfg = {}
    for p in cfg_paths:
        if p.exists():
            try:
                with p.open() as f:
                    loaded = yaml.safe_load(f) or {}
                    if isinstance(loaded, dict):
                        cfg = loaded
                        break
            except Exception as e:
                LOG.debug(f"Could not read config.yaml at {p}: {e}")

    attempts = defaults['attempts']
    wait_seconds = defaults['wait_seconds']

    # From config.yaml
    if isinstance(cfg.get('retry'), dict):
        attempts = int(cfg['retry'].get('attempts', attempts))
        wait_seconds = int(cfg['retry'].get('wait_seconds', wait_seconds))

    # Overlay env
    env_attempts = os.getenv('RETRY_ATTEMPTS')
    env_wait = os.getenv('RETRY_WAIT')
    try:
        if env_attempts is not None:
            attempts = int(env_attempts)
    except ValueError:
        LOG.warning(f"Invalid RETRY_ATTEMPTS={env_attempts!r}; using {attempts}")
    try:
        if env_wait is not None:
            wait_seconds = int(env_wait)
    except ValueError:
        LOG.warning(f"Invalid RETRY_WAIT={env_wait!r}; using {wait_seconds}")

    return attempts, wait_seconds


def retry(attempts=None, wait_seconds=None, allowed_exceptions=(Exception,)):
    """Custom retry decorator with detailed logging for each attempt.

    If attempts/wait_seconds are not provided, they are loaded from env/config.

    Usage:
        @retry()  # uses config/env defaults
        @retry(attempts=3, wait_seconds=2)  # explicit override
        def call():
            ...
    """
    if attempts is None or wait_seconds is None:
        cfg_attempts, cfg_wait = _load_retry_defaults()
        attempts = cfg_attempts if attempts is None else attempts
        wait_seconds = cfg_wait if wait_seconds is None else wait_seconds

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                start = time.time()
                try:
                    LOG.info(f"Attempt {attempt}/{attempts} for {func.__name__}")
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    LOG.info(f"Success on attempt {attempt} in {duration:.2f}s")
                    return result
                except allowed_exceptions as e:
                    duration = time.time() - start
                    LOG.warning(
                        f"Attempt {attempt} failed for {func.__name__} in {duration:.2f}s: {e!r}"
                    )
                    last_exc = e
                    if attempt < attempts:
                        LOG.info(f"Waiting {wait_seconds}s before next attempt...")
                        time.sleep(wait_seconds)
            LOG.error(f"All {attempts} attempts failed for {func.__name__}")
            raise RetryException(f"{func.__name__} failed after {attempts} attempts") from last_exc
        return wrapper
    return decorator