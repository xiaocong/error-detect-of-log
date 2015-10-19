from utils import detect_string, gen_hashcode, jsonify_headers


KERNEL_PANIC = [
    r"(kernel BUG at[^\n]+)",
    r"(spinlock bad magic)",
    r"(Unable to handle kernel[^\n]+)",
    r"(modem subsystem failure reason:.*Could not turn on the UNIV_STMR ustmr_qtimer_off_counter)",
    r"(\w+ subsystem failure reason:[^\n]+)",
    r"(Kernel panic - not syncing: [^\n]*: Timed out waiting for error ready: modem)",
    r"(Kernel panic - [^\n]*)"
]

IGNORES = [
    r"Crash injected via Diag",
    r"SysRq : Trigger a crash"
]


def kernel_panic(logcat, headers):
    parts = logcat.split('\n\n')
    for content in parts[1:]:
        process = "kernel"
        for ignore in IGNORES:
            if detect_string(content, ignore):
                return None, None, None
        for pattern in KERNEL_PANIC:
            reason = detect_string(content, pattern)
            if reason:
                result = {'issue_owner': process, 'detail': reason}
                if "ramdump" in reason:
                    try:
                        UA = jsonify_headers(headers.get('X-Dropbox-UA', '='))
                        if UA.get("buildtype") == "user" or UA.get("type") == "user" or UA.get("build_type") == "user":
                            return None, None, None
                        for key in ['imei', 'mac_address', 'sn', 'phone_number']:
                            if UA.get(key):
                                result[key] = UA.get(key)
                    except:
                        pass
                md5 = gen_hashcode(result)
                return md5, result, None
    return None, None, None
