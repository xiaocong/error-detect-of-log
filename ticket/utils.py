# -*- coding: utf-8 -*-

import json


def check_request_data(data):
    data = json.loads(data)
    if not data.get('type'):
        return False
    if not data.get('url'):
        return False
    if not data.get('username'):
        return False
    if not data.get('password'):
        return False
    return data
