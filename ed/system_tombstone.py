# -*- coding: utf-8 -*-

import re
from utils import detect_string, gen_hashcode, detect_all
from symbols import translate_traces


IGNORE = ['/data/app-lib', '/mnt/asec/', '/data/data/', '/data/app/']


def detect_trace(contents):
    for content in contents:
        if "backtrace:" in content:
            backtrace = detect_all(content, r'((?:/.+)+(?: \(.+\))*)')
            if backtrace:
                for bt in backtrace:
                    for ig in IGNORE:
                        if ig in bt:
                            return []
                return backtrace, content
    return None, None


def detect_issue_owner(backtrace):
    if backtrace:
        for bt in backtrace:
            if '(' in bt:
                lib = bt.split('(')[0].strip()
                break
        else:
            lib = backtrace[0]
        ret = lib.split('/')[-1] if '/' in lib else lib
        return None if '<unknown>' in ret else ret


def match_version(content):
    return detect_string(content[0], r'^Build:.+/(\d+\.\d+)/') == detect_string(content[1], r'^Build\s+fingerprint:.+/(\d+\.\d+)/')


def system_tombstone(logcat, headers):
    content = logcat.split('\n\n')
    if len(content) >= 3:
        if not match_version(content):
            return None, None, None
        signal = detect_string(content[1], r'^(signal\s+-?\d+\s+\(\w+\),\s+code\s+-?\d+\s+\(\w+\))')
        backtrace, raw_bt = detect_trace(content[2:])
        issue_owner = detect_issue_owner(backtrace)
        if issue_owner and signal and backtrace:
            traces = translate_traces(headers, raw_bt)
            md5 = gen_hashcode({'issue_owner': issue_owner, 'signal': signal, 'backtrace': backtrace})
            return md5, {'issue_owner': issue_owner, 'signal': signal, 'backtrace': backtrace}, traces
    return None, None, None
