import requests
from utils.retry import retry


@retry(attempts=10, wait_seconds=1)
def get_json(url, timeout=10):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r


def test_get_json_returns_valid_json(base_url, config):
    url = f"{base_url}/json"
    r = get_json(url, timeout=config['default_timeout'])
    # verify content-type header and parse
    assert 'application/json' in r.headers.get('Content-Type', '')
    data = r.json()
    assert isinstance(data, dict)
    # Expect that the top-level has 'slideshow' (httpbin specific)
    assert 'slideshow' in data


def test_get_xml_format(base_url, config):
    url = f"{base_url}/xml"
    r = requests.get(url, timeout=config['default_timeout'])
    r.raise_for_status()
    assert 'xml' in r.headers.get('Content-Type', '')
    assert r.text.strip().startswith('<?xml')