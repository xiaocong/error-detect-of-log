
# -*- coding: utf-8 -*-

from jira.client import JIRA
import re


class JiraHandler(object):

    def __init__(self, data):
        self.myjira = JIRA(options={'server': data['url']}, basic_auth=(data['username'], data['password']))


    def get_ticket(self, ticket_id):
        return self.myjira.issue(ticket_id)


    def compare_sys_ver(self, sys_ver, fixed_ver):
        if int(sys_ver.split('.')[0]) != int(fixed_ver.split('.')[0]):
            return int(sys_ver.split('.')[0]) > int(fixed_ver.split('.')[0])
        else:
            return int(sys_ver.split('.')[1]) > int(fixed_ver.split('.')[1])


    def detect_comments_vers(self, issue):
        ret = []
        for com in issue.fields.comment.comments:
            if com.author.name == self.myjira.current_user():
                match = re.findall(r'\s+(\d+(?:\.\d+)+(?:\/\d+)?)\s+', com.body)
                if match:
                    ret.append(match[0])
        return ret


    def detect_max_ver(self, issue):
        if issue.fields.versions:
            target_vers = [ver.name for ver in issue.fields.versions]
            target_vers.extend(self.detect_comments_vers(issue))
            if len(target_vers) > 1:
                maxver = ""
                for i in range(len(target_vers) - 1):
                    maxver = target_vers[i+1] if self.compare_sys_ver(target_vers[i], target_vers[i+1]) else target_vers[i]
                return maxver
            return target_vers[0]
        return None


    def get_ticket_status(self, data):
        ticket_id = data.get('ticket_id')
        sys_ver = data.get('sys_ver')
        issue = self.get_ticket(ticket_id)
        if issue.fields.resolution:
            if issue.fields.resolution.name == "Duplicate":
                issue = self.root_ticket_detector(ticket_id)
            if issue:
                if issue.fields.resolution:
                    if issue.fields.resolution.name == 'Cannot Reproduce':
                        if self.compare_sys_ver(sys_ver, self.detect_max_ver(issue)):
                            return 0, 'reopen'
                    elif issue.fields.resolution.name == 'Fixed':
                        if issue.fields.status.name in ['Closed', 'Integrated']:
                            if issue.fields.fixVersions:
                                if self.compare_sys_ver(sys_ver, issue.fields.fixVersions[0].name):
                                    return 0, 'reopen'
                            else:
                                return 0, 'no-fix-version'
                else:
                    return 0, 'append-dropbox-id'
            else:
                return 0, 'idle'
        else:
            return 0, 'append-dropbox-id'
        return 0, 'idle'


    def root_ticket_detector(self, ticket_id):
        ticket_ids = ticket_id if type(ticket_id) is list else [ticket_id]
        for i in range(100): #TODO: tmp solution for the dead dup issue
            tmp_ticket_ids = []
            for ticket_id in ticket_ids:
                issue = self.get_ticket(ticket_id)
                targetkey = None
                if len(issue.fields.issuelinks) == 0:
                    return None
                for dupissue in issue.fields.issuelinks:
                    try:
                        rootissue = self.get_ticket(dupissue.outwardIssue.key)
                    except AttributeError:
                        rootissue = self.get_ticket(dupissue.inwardIssue.key)
                    if not rootissue.fields.resolution or rootissue.fields.resolution.name != "Duplicate":
                        targetkey = rootissue.key
                        break
                    tmp_ticket_ids.append(rootissue.key)
                if targetkey:
                    break
            if targetkey:
                break
            ticket_ids = tmp_ticket_ids
        if targetkey:
            return self.get_ticket(targetkey)


    def reopen_ticket(self, data):
        issue = self.get_ticket(data.get('ticket_id'))
        options = self.myjira.transitions(issue)
        for option in options:
            if option.get('name') == 'Reopen':
                self.myjira.transition_issue(issue, option.get('id'))
                return 0, 'ok'
        else:
            return 1, 'ticket is open, how to reopen it?'


    def add_comment(self, data):
        issue = self.get_ticket(data.get('ticket_id'))
        self.myjira.add_comment(issue, data.get('comment'))
        return 0, 'ok'


    def valide_project(self, req_proj):
        projects = self.myjira.projects()
        for project in projects:
            if req_proj == project.key:
                return True
        else:
            return False


    def get_proj_components(self, data):
        if self.valide_project(data.get('proj')):
            return 0, [comp.name for comp in self.myjira.project_components(data.get('proj'))]
        else:
            return 1, []


    def create_proj_component(self, data):
        if self.valide_project(data.get('proj')):
            cur_comps = [comp.name for comp in self.myjira.project_components(data.get('proj'))]
            if data.get('comp') in cur_comps:
                return 0, "required comp. exist already"
            else:
                self.myjira.create_component(name=data.get('comp'), project=data.get('proj'))
                return 0, 'created'
        return 1, 'invalid proj.'


    def valide_component(self, proj, cur_comp):
        components = [comp.name for comp in self.myjira.project_components(proj)]
        if not cur_comp in components:
            if not "Triage" in components:
                self.myjira.create_component(name="Triage", project=proj)
            return "Triage"
        return cur_comp


    def valide_sys_ver(self, proj, sys_ver):
        for version in self.myjira.project_versions(proj):
            if version.name == sys_ver:
                break
        else:
            self.myjira.create_version(name=sys_ver, project=proj)


    def gen_url(self, data, ticket_id):
        if data.get('url').endswith('/'):
            return data.get('url') + 'browse/' + ticket_id
        else:
            return data.get('url') + '/browse/' + ticket_id


    def create_ticket(self, data):
        if self.valide_project(data.get('proj')):
            comp = self.valide_component(data.get('proj'), data.get('comp'))
            self.valide_sys_ver(data.get('proj'), data.get('sys_ver'))
            new_issue = self.myjira.create_issue(
                project={'key': data.get('proj')},
                versions=[{'name': data.get('sys_ver')}],
                components=[{'name': comp}],
                issuetype={'name': 'Bug'},
                summary=data.get('summary'),
                description=data.get('description')
            )
            return 0, {'ticket_id': new_issue.key, 'url': self.gen_url(data, new_issue.key)}
        return 1, None