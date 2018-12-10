from urllib.error import HTTPError
from urllib.request import Request, urlopen

import json

_API_URL = 'https://build-system.fman.io/api/'

def post_json(path, data, encoding='utf-8'):
    # We could just use the requests library. But it doesn't pay off to add the
    # whole dependency for just this one function.
    request = Request(_API_URL + path)
    request.add_header('Content-Type', 'application/json; charset=' + encoding)
    data_bytes = json.dumps(data).encode(encoding)
    request.add_header('Content-Length', len(data_bytes))
    try:
        with urlopen(request, data_bytes) as response:
            return response.getcode(), response.read().decode(encoding)
    except HTTPError as e:
        return e.getcode(), e.fp.read().decode(encoding)