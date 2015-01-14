# -*- coding: utf-8 -*-

import os
import json
from flask import Flask, jsonify, request
from docopt import docopt
from ed import *

TAGS = {
    "system_app_crash": app_crash,
    "SYSTEM_TOMBSTONE": system_tombstone,
    "system_app_wtf":   app_wtf,
    "system_app_anr":   app_anr,
}


def root(p=None):
    if p is not None and os.path.isabs(p):
        return p
    self_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(self_dir, p) if p else self_dir


def make_console_log_handler():
    import logging
    import sys
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))


DOCOPT = """
        Feature Detector: Start server

        Usage:
            server.py -c=<config_path>
            server.py (-h | --help)
            server.py --version

        Options:
            -c=<config_path>    /path/to/config1
            -h --help           Show this screen
            --version           Show version
        """

opts = docopt(DOCOPT, version='v1')
app = Flask(__name__)
app.config.from_pyfile(root(opts['-c']))
app.logger.addHandler(make_console_log_handler())


@app.errorhandler(500)
def error_500_handler():
    return jsonify(status=0, msg="server 500 error", features={})


@app.errorhandler(Exception)
def exception_handler():
    return jsonify(status=0, msg='server exception', features={})


@app.route('/api/detect/<tag>', methods=['POST'])
def api_detect(tag):
    if not tag in TAGS.keys():
        return jsonify(status=0, msg='tag not supported', features={})
    try:
        data = request.data
        if data:
            features = TAGS[tag](data)
            if features:
                return jsonify(status=1, msg='feature detected', features=features)
            else:
                return jsonify(status=0, msg='failed to detect features', features={})
        else:
            return jsonify(status=0, msg='logcat field required', features={})
    except Exception:
        return jsonify(status=0, msg='failed to detect features', features={})


def run_app(app_):
    host, port = '0.0.0.0', app_.config.get('SERVER_PORT', 9786)
    if app_.config.get('DEBUG', False):
        app_.logger.info("* run: flask")
        app_.run(host=host, port=port)
    else:
        try:
            import gunicorn.app.base

            class GunicornApp(gunicorn.app.base.Application):
                def __init__(self, app, opts):
                    self.app, self.opts = app, opts
                    super(GunicornApp, self).__init__()

                def load_config(self):
                    cfg = gunicorn.app.base.Config()
                    for k, v in self.opts.items():
                        cfg.set(k, v)
                    self.cfg = cfg

                def load(self):
                    return self.app

            opts = dict(
                bind='%s:%s' % (host, port),
                workers=app_.config.get('GUNICORN_WORKERS', 1),
            )
            app_.logger.info("* run: gunicorn")
            GunicornApp(app_, opts).run()
        except ImportError:
            app_.logger.info("* run: flask")
            app_.run(host=host, port=port)


if __name__ == "__main__":
    run_app(app)
