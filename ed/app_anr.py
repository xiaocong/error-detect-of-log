# -*- coding: utf-8 -*-

import re
from utils import detect_string, gen_hashcode

IOWAIT_THRESHOLD = 35.0
TOTAL_THRESHOLD = 40.0


def detect_keyword(exp, content, mode=0):
    match = re.findall(exp, content)
    if mode == 1:
        return match if match else []
    return match[0] if match else None


def java_binder(cpu_usage, mainstack, process):
    detail = detect_keyword(r'\s+at\s+android\.os\.BinderProxy\.transact\(Native Method\)\n\s+(at\s+.+)\n', mainstack)
    if detail:
        return process, detail, None
    return None, None, None


def system_busy(cpu_usage, mainstack, process):
    total = detect_keyword(r'(\d+(?:\.\d+)?)\%\s+TOTAL', cpu_usage)
    iowait = detect_keyword(r'(\d+(?:\.\d+)?)\%\s+iowait', cpu_usage)
    if iowait and float(iowait) >= IOWAIT_THRESHOLD:
        return "iowait", "CPU usage: iowait >= 35%", None
    if total and float(total) >= TOTAL_THRESHOLD:
        topprocess = detect_keyword(r'\s+\d+(?:\.\d+)?\%\s+(?:\d+)?/([\w-]+(?:\.[\w-]+)*)', cpu_usage)
        return topprocess, ("CPU usage: TOTAL >= 40%, " + topprocess + " occupied the most."), None
    return None, None, None


def native_binder(cpu_usage, mainstack, process):
    details = detect_keyword(r'\s+((?:/.+)+(?:\s+\(.+\))?)', mainstack, 1)
    binder = False
    for detail in details:
        if not binder and 'libbinder.so' in detail:
            binder = True
        if binder and 'libbinder.so' not in detail:
            for key in ['libmedia\.so', 'libtvmanager\.so', 'libaudiomanager\.so', 'libgui\.so', 'libsystem_server\.so', 'libchannelmanager\.so']:
                if detect_keyword((r'%s\s+\(.+\)' %(key)), detail):
                    return key.replace("\\", ""), detail, None
    return None, None, None


def native_lock(cpu_usage, mainstack, process):
    details = detect_keyword(r'\s+((?:/.+)+(?:\s+\(.+\))?)', mainstack, 1)
    lock = False
    for detail in details:
        if not lock and 'libc.so (__futex_syscall' in detail:
            lock = True
        if lock and 'libc.so' not in detail:
            return process, detail, None
    return None, None, None


def java_lock(cpu_usage, mainstack, process):
    for exp in [r'\s+-\s+(waiting\s+on\s+<.+>\s+(?:\(a\s+\w+(?:[.$]\w+)+\))?)', r'\s+-\s+(waiting\s+to\s+lock\s+<.+>\s+(?:\(a\s+\w+(?:[.$]\w+)+\))?)']:
        detail = detect_keyword(exp, mainstack)
        if detail:
            return process, re.sub(r'<\w+>', 'addr.', detail), None
    return None, None, None


def mthread_busy(cpu_usage, mainstack, process):
    for exp in [r'\s+(at\s+java\.io\..+)', r'\s+(at\s+android\.database\.sqlite\..+)']:
        detail = detect_keyword(exp, mainstack)
        if detail:
            return process, detail, None
    return None, None, None


def auto_recover(cpu_usage, mainstack, process):
    details = detect_keyword(r'\s+(at\s+\w+(?:[.$]\w+)+(?:\(.+\))?)', mainstack, 1)
    if details and "android.os.MessageQueue.nativePollOnce" in details[0]:
        return None, None, "RECOVER"
    return None, None, None


def detect_basic_info(logcat):
    process, cpu_usage, mainstack = None, None, None
    for minor_part in logcat.split('\n\n'):
        if not process:
            process = detect_string(minor_part, r'^Process:\s+(\w+(?:[.$_]\w+)+)')
        if not cpu_usage and detect_string(minor_part, r'(CPU\s+usage\s+from\s+-?\w+\s+to\s+-?\w+)'):
            cpu_usage = minor_part
        if not mainstack and detect_string(minor_part, r'^(\"main\")\s+'):
            mainstack = minor_part
    return process, cpu_usage, mainstack


METHODS = [java_binder, system_busy, native_binder, native_lock, java_lock, mthread_busy, auto_recover]


def app_anr(logcat, headers):
    process, cpu_usage, mainstack = detect_basic_info(logcat)
    if process and cpu_usage and mainstack:
        for method in METHODS:
            process, detail, tag = method(cpu_usage, mainstack, process)
            if tag == "RECOVER":
                break
            if process and detail:
                md5 = gen_hashcode({'issue_owner': process, 'detail': detail})
                return md5, {'issue_owner': process, 'detail': detail}, None
    return None, None, None
