# -*- coding: utf-8 -*-

from utils import detect_string, gen_hashcode


def detect_detail(raw_string, process):
    length = len(process.split("."))
    for i in range(length - 1):
        for line in raw_string.split('\n'):
            match = detect_string(line, r'\t(at\s+(%s){1}.*)' % (".".join(process.split(".")[:(length - i)])))
            if match:
                return match
    return detect_string(raw_string, r'\s+(at\s+(?:.)*)')


def app_crash(logcat, headers):
    content = logcat.split('\n\n')
    if len(content) >= 2:
        process = detect_string(content[0], r'^Process:\s+(\w+(?:[.$_]\w+)+)')
        exception = detect_string(content[1], r'^(\w+(?:[.$_]\w+)+)')
        if process:
            detail = detect_detail(content[1], process)
            if exception and detail:
                md5 = gen_hashcode({'issue_owner': process, 'exception': exception, 'detail': detail})
                return md5, {'issue_owner': process, 'exception': exception, 'detail': detail}, None
    return None, None, None
