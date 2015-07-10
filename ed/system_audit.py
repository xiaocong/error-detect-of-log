from utils import gen_hashcode
import re


def system_audit(logcat, headers):
    parts = logcat.split('\n\n')

    process = "system_audit"
    content = "\n".join(parts[1:])
    types = re.findall(r"type=(\d+)", content)
    types = filter(lambda x: x != "2000", sorted(list(set(types))))
    if len(types) > 0:
        result = {'issue_owner': process, 'detail': "system audit failure types: " + ", ".join(types)}
        md5 = gen_hashcode(result)
        return md5, result, None
    return None, None, None
