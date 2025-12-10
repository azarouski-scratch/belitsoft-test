import requests
from utils.faker_utils import random_person


def test_post_inspect_headers_and_json(base_url, config):
    url = f"{base_url}/post"
    payload = random_person()
    headers = {'X-Test-Run': 'automation', 'Content-Type': 'application/json'}
    r = requests.post(url, json=payload, headers=headers, timeout=config['default_timeout'])
    r.raise_for_status()
    data = r.json()
    # httpbin returns our json under 'json'
    assert data['json'] == payload
    # and headers are echoed under 'headers'
    assert data['headers']['X-Test-Run'] == 'automation'


def test_get_inspect_query_params(base_url, config):
    params = {'q': 'pytest', 'page': 2}
    r = requests.get(f"{base_url}/get", params=params, timeout=config['default_timeout'])
    r.raise_for_status()
    data = r.json()
    assert data['args']['q'] == 'pytest'
    assert data['args']['page'] == '2'