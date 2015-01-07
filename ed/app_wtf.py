# -*- coding: utf-8 -*-

from utils import detect_string


def app_wtf(logcat):
    content = logcat.split('\n\n')
    if len(content) == 2:
        process = detect_string(content[0], r'^Process:\s+(\w+(?:[.$_]\w+)+)')
        exception = detect_string(content[1], r'^(\w+(?:[.$_]\w+)+)')
        detail = detect_string(content[1], r'\t(at\s+android\.util\.Log\.wtf.*)')
        if process and exception and detail:
            return {'issue_owner': process, 'exception': exception, 'detail': detail}
    return {}
