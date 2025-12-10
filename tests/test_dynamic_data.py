import requests
from utils.faker_utils import random_person, random_text


def test_dynamic_put_and_get(base_url, config):
    url = f"{base_url}/put"
    payload = random_person()
    payload['bio'] = random_text(2)
    r = requests.put(url, json=payload, timeout=config['default_timeout'])
    r.raise_for_status()
    data = r.json()
    assert data['json']['email'] == payload['email']
    assert 'bio' in data['json']