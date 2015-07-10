# -*- coding: utf-8 -*-

import os
import subprocess
from utils import detect_all, jsonify_headers
import requests

TOOLPATH = '/home/xinqiserver1/android-ndk-r9d/toolchains/arm-linux-androideabi-4.6/prebuilt/linux-x86_64/bin/arm-linux-androideabi-addr2line'


def valide_headers(headers):
    UA = headers.get('X-Dropbox-UA')
    if UA:
        UA = jsonify_headers(UA)
        if not UA.get('product'):
            return False
        if not UA.get('build_id'):
            return False
        if not UA.get('type'):
            return False
        if not UA.get('file_path', '/file1/cm'):
            return False
        return UA
    return False


def translate_traces(headers, raw_bt):
    UA = valide_headers(headers)
    if not UA:
        return None
    addr_libs = detect_all(raw_bt, r'\s+(\w+\s+(?:/.+)+)\s+')
    traces = []
    for addr_lib in addr_libs:
        symbol_path = '/'.join([UA.get('file_path', '/file1/cm'), UA['product'], UA['build_id'], UA['type'], 'symbols', addr_lib.split(' ')[2]])
        if os.path.exists(symbol_path) and os.path.exists(TOOLPATH):
            cmd = ' '.join([TOOLPATH, '-f -e', symbol_path, addr_lib.split(' ')[0]])
            p = subprocess.Popen(cmd.split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = p.stdout.readlines()
            for line in lines:
                if "??" in line:
                    break
            else:
                traces.append("%s at %s" % (lines[0], lines[1]))
    return traces


def backtrace(ua, body):
    headers = {
        "X-Dropbox-UA": ua
    }
    try:
        r = requests.post("http://localhost:8800", headers=headers, data=body)
        print r.text
        return r.json().get("backtrace") or []
    except:
        return []
