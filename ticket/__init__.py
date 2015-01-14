# -*- coding: utf-8 -*-

from flask import jsonify, request
from jira_handler import JiraHandler
from utils import check_request_data


OBJS = {'jira': JiraHandler}


def get_ticket_status():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, action = OBJS[data['type']](data).get_ticket_status(data)
        return jsonify(code=code, data={'action': action}, msg='')
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def reopen_ticket():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, ret = OBJS[data['type']](data).reopen_ticket(data)
        return jsonify(code=code, data={}, msg=ret)
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def add_comment():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, ret = OBJS[data['type']](data).add_comment(data)
        return jsonify(code=code, data={}, msg=ret)
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def get_proj_components():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, ret = OBJS[data['type']](data).get_proj_components(data)
        return jsonify(code=code, data={'components': ret}, msg='')
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def create_proj_component():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, ret = OBJS[data['type']](data).create_proj_component(data)
        return jsonify(code=code, data={}, msg=ret)
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def create_ticket():
    data = check_request_data(request.data)
    if data and data['type'] in OBJS.keys():
        code, ret = OBJS[data['type']](data).create_ticket(data)
        return jsonify(code=code, data=ret, msg='')
    else:
        return jsonify(code=1, data={}, msg='required fields missing or illegal')


def setup_ticket(app):
    app.add_url_rule('/api/ticket/status/get', 'get_ticket_status', get_ticket_status, methods=['POST'])
    app.add_url_rule('/api/ticket/status/reopen', 'reopen_ticket', reopen_ticket, methods=['POST'])
    app.add_url_rule('/api/ticket/comment/add', 'add_comment', add_comment, methods=['POST'])
    app.add_url_rule('/api/project/components/get', 'get_proj_components', get_proj_components, methods=['POST'])
    app.add_url_rule('/api/project/components/create', 'create_proj_component', create_proj_component, methods=['POST'])
    app.add_url_rule('/api/ticket/create', 'create_ticket', create_ticket, methods=['POST'])