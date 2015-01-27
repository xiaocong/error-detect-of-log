# -*- coding: utf-8 -*-

import re
import hashlib


def detect_string(raw_string, exp):
    match = re.search(exp, raw_string, re.MULTILINE)
    return match.groups()[0] if match else None


def gen_hashcode(data):
    return hashlib.md5(str(data)).hexdigest()


def detect_all(raw_string, exp):
    return re.findall(exp, raw_string, re.MULTILINE)


def jsonify_headers(raw_string):
    ret = {}
    for kv in raw_string.split(';'):
        ret[kv.split('=')[0]] = kv.split('=')[1]
    return ret
