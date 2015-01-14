# -*- coding: utf-8 -*-

import re
from utils import detect_string, gen_hashcode


def detect_trace(contents):
    for content in contents:
        if "backtrace:" in content:
            return re.findall(r'((?:/.+)+(?: \(.+\))*)', content)


def detect_issue_owner(backtrace):
    if backtrace:
        for bt in backtrace:
            if '(' in bt:
                lib = bt.split('(')[0].strip()
                break
        else:
            lib = backtrace[0]
        return lib.split('/')[-1] if '/' in lib else lib


def system_tombstone(logcat):
    content = logcat.split('\n\n')
    if len(content) >= 3:
        #process = detect_string(content[1], r'\s+>>>\s+(.*)\s+<<<')
        signal = detect_string(content[1], r'^(signal\s+\d+\s+\(\w+\),\s+code\s+\d+\s+\(\w+\))')
        backtrace = detect_trace(content[2:])
        issue_owner = detect_issue_owner(backtrace)
        if issue_owner and signal and backtrace:
            md5 = gen_hashcode({'issue_owner': issue_owner, 'signal': signal, 'backtrace': backtrace})
            return md5, {'issue_owner': issue_owner, 'signal': signal, 'backtrace': backtrace}
    return {}
