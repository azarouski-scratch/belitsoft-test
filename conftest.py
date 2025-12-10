import os
import logging
import yaml
import pytest
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

LOG = logging.getLogger(__name__)

def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@pytest.fixture(scope='session')
def config():
    """Load configuration from YAML and environment with sensible defaults.

    Precedence: environment variables override YAML values; YAML overrides defaults.
    Supported env vars: BASE_URL, DEFAULT_TIMEOUT, RETRY_ATTEMPTS, RETRY_WAIT, ENV, API_KEY.
    """
    base = Path(__file__).parent
    cfg_path = base / 'config.yaml'

    cfg: dict = {}
    if cfg_path.exists():
        try:
            with cfg_path.open() as f:
                loaded = yaml.safe_load(f) or {}
                if not isinstance(loaded, dict):
                    LOG.warning("config.yaml did not contain a mapping; ignoring it")
                    loaded = {}
                cfg.update(loaded)
        except Exception as e:
            LOG.error(f"Failed to read config.yaml: {e}")
    else:
        LOG.info("config.yaml not found; relying on environment and defaults")

    # Defaults
    defaults = {
        'base_url': 'http://localhost:80',
        'default_timeout': 10,
        'retry': {
            'attempts': 3,
            'wait_seconds': 1,
        },
    }

    # Start with defaults, then YAML
    merged = {
        'base_url': cfg.get('base_url', defaults['base_url']),
        'default_timeout': cfg.get('default_timeout', defaults['default_timeout']),
        'retry': {
            'attempts': (cfg.get('retry', {}) or {}).get('attempts', defaults['retry']['attempts']),
            'wait_seconds': (cfg.get('retry', {}) or {}).get('wait_seconds', defaults['retry']['wait_seconds']),
        },
    }

    # Overlay env vars
    env_base_url = os.getenv('BASE_URL')
    env_default_timeout = os.getenv('DEFAULT_TIMEOUT')
    env_retry_attempts = os.getenv('RETRY_ATTEMPTS')
    env_retry_wait = os.getenv('RETRY_WAIT')

    if env_base_url:
        merged['base_url'] = env_base_url.rstrip('/')
    merged['default_timeout'] = _to_int(env_default_timeout, merged['default_timeout'])
    merged['retry']['attempts'] = _to_int(env_retry_attempts, merged['retry']['attempts'])
    merged['retry']['wait_seconds'] = _to_int(env_retry_wait, merged['retry']['wait_seconds'])

    # Additional env-only settings
    merged['env'] = os.getenv('ENV', cfg.get('env', 'local'))
    merged['api_key'] = os.getenv('API_KEY', cfg.get('api_key'))

    LOG.info(
        "Loaded config",
        extra={
            'env': merged['env'],
            'base_url': merged['base_url'],
            'default_timeout': merged['default_timeout'],
            'retry_attempts': merged['retry']['attempts'],
            'retry_wait_seconds': merged['retry']['wait_seconds'],
        },
    )
    return merged


@pytest.fixture
def base_url(config):
    return config['base_url']