# -*- coding: utf-8 -*-

import re
from utils import detect_string


def detect_trace(contents):
    for content in contents:
        if "backtrace:" in content:
            return re.findall(r'((?:/.+)+(?: \(.+\))*)', content)


def system_tombstone(logcat):
    content = logcat.split('\n\n')
    if len(content) >= 3:
        process = detect_string(content[1], r'\s+>>>\s+(.*)\s+<<<')
        signal = detect_string(content[1], r'^(signal\s+\d+\s+\(\w+\),\s+code\s+\d+\s+\(\w+\))')
        backtrace = detect_trace(content[2:])
        if process and signal and backtrace:
            return {'process': process, 'signal': signal, 'backtrace': backtrace}
    return {}
