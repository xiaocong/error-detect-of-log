# -*- coding: utf-8 -*-

from utils import detect_string, gen_hashcode


def detect_detail(content):
    detail = detect_string(content, r'^\t(at\s+android\.util\.Log\.wtf.*)$')
    if not detail:
        detail = detect_string(content, r'^\t(at\s+.+)$')
    return detail


def app_wtf(logcat, headers):
    content = logcat.split('\n\n')
    if len(content) >= 2:
        process = detect_string(content[0], r'^Process:\s+(\w+(?:[.$_]\w+)+)')
        exception = detect_string(content[1], r'^(\w+(?:[.$_]\w+)+)')
        detail = detect_detail(content[1])
        if process and exception and detail:
            md5 = gen_hashcode({'issue_owner': process, 'exception': exception, 'detail': detail})
            return md5, {'issue_owner': process, 'exception': exception, 'detail': detail}, None
    return None, None, None
