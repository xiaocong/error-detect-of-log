
import os.path
from ed import system_tombstone


def test_tombstone():
    with open(os.path.join(os.path.dirname(__file__), 'dropbox/tombstone_1.txt')) as f:
        log = f.read()
        md5, result = system_tombstone(log)
        assert len(result.keys()) > 0
        assert 'backtrace' in result.keys()
        assert 'signal' in result.keys()
        assert 'issue_owner' in result.keys()


if __name__ == "__main__":
    test_tombstone()
