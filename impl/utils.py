# -*- coding: utf-8 -*-

import re


def detect_string(raw_string, exp):
    match = re.search(exp, raw_string, re.MULTILINE)
    return match.groups()[0] if match else None