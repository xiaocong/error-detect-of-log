from utils import detect_string, gen_hashcode


def system_server_watchdog(logcat, headers):
    parts = logcat.split('\n\n')
    head = parts[0]
    process = detect_string(head, r"Process:\s+(\w+)")
    subject = detect_string(head, r"Subject:\s+([^\n]+)")
    if process and subject:
        result = {'issue_owner': process, 'subject': subject}
        md5 = gen_hashcode(result)
        return md5, result, None
    return None, None, None
