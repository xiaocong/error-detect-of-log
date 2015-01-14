# -*- coding: utf-8 -*-

import re
import hashlib


def detect_string(raw_string, exp):
    match = re.search(exp, raw_string, re.MULTILINE)
    return match.groups()[0] if match else None


def gen_hashcode(data):
    return hashlib.md5(str(data)).hexdigest()
