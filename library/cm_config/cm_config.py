#!/usr/bin/env python
# cm_config: Manage Cloudera Manager configuration


DOCUMENTATION = """
---
module: cm_config

author:
    - Khanh-Toan Tran (khtoantran[at]gmail.com)

short_description: Manage Cloudera Manager configuration

description:
    - Manage Cloudera Manager configuration

version_added: "2.0"

options:
    cm_url:
      description:
        - URL for Cloudera Manager
      required: true
      default: null
    cm_username:
      description:
        - User for Cloudera Manager
      required: true
      default: null
    cm_password:
      description:
        - Password for Cloudera Manager
      required: true
      default: null
    name:
      description:
        - Configuration key to change
      required: false
      default: null
    value:
      description:
        - Value of the configuration, only used when action is set
      required: false
      default: null
    action:
      description:
        - Action to take
      required: false
      default: get
      choices: ['get', 'set', 'delete']
    view:
      description:
        - Should return full information or a summary, only used when action is get
      required: false
      default: summary
      choices: ['full', 'summary']
"""

RETURNS = """
    status_code:
        description: Status of HTTP Response from Cloudera Manager.
        type: int
    msg:
        description: Message from Cloudera Manager, or an Error message
        type: string
    content:
        description: Returned content of the command if action is get; empty for other cases. For easy parse the result.
        type: dict
"""

EXAMPLES = """
- hosts: localhost
  vars:
    cm_url: http://localhost:7180
    cm_username: admin
    cm_password: admin
  tasks:
    - name: Get config key null with summary view - should return all modified configs
      cm_config:
        cm_username: "{{ cm_username }}"
        cm_password: "{{ cm_password }}"
        cm_url: "{{ cm_url }}"
        action: get
      register: cm_summary_config

    - name: Get all config key with full view
      cm_config:
        cm_username: "{{ cm_username }}"
        cm_password: "{{ cm_password }}"
        cm_url: "{{ cm_url }}"
        action: get
        view: full
      register: cm_all_config

    - name: Show all CM config
      debug: msg="There are {{ cm_config['content']['items'] | length}} configuration items in Cloudera Manager"

    - name: Get CLUSTER_STATS_START and CLUSTER_STATS_SCHEDULE configuration with full view
      cm_config:
        cm_username: "{{ cm_username }}"
        cm_password: "{{ cm_password }}"
        cm_url: "{{ cm_url }}"
        action: get
        name: "CLUSTER_STATS_START,CLUSTER_STATS_SCHEDULE"
        view: full
      register: cm_config_stat_view_full

    - name: Set CLUSTER_STATS_SCHEDULE to MONTHLY
      cm_config:
        cm_username: "{{ cm_username }}"
        cm_password: "{{ cm_password }}"
        cm_url: "{{ cm_url }}"
        action: set
        name: "CLUSTER_STATS_SCHEDULE"
        value: "MONTHLY"
      register: cm_config_cluster_stats_schedule

    - name: Delete CLUSTER_STATS_SCHEDULE and PARCEL_DISTRIBUTE_RATE_LIMIT_KBS_PER_SECOND
      cm_config:
        cm_username: "{{ cm_username }}"
        cm_password: "{{ cm_password }}"
        cm_url: "{{ cm_url }}"
        action: delete
        name: "CLUSTER_STATS_SCHEDULE,PARCEL_DISTRIBUTE_RATE_LIMIT_KBS_PER_SECOND"
      register: cm_config_delete_cluster_stats_schedule
"""


import httplib2
import json

from ansible.module_utils.basic import *


def _return_error(resp, respb):
    """Return an error status if the status is not 200."""
    global module
    if resp.status != 200:
        module.fail_json(changed=False,
                         status_code=resp.status,
                         content=dict(),
                         msg=respb)


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            cm_url=dict(required=True, type='str'),
            cm_username=dict(required=True, type='str'),
            cm_password=dict(required=True, type='str', no_log=True),
            name=dict(required=False, type='str'),
            value=dict(required=False, type='str'),
            action=dict(choices=['set', 'delete', 'get'], type='str', default='get'),
            view=dict(choices=['full', 'summary'], type='str', default='summary')
        )
    )

    cm_url = module.params.get('cm_url')
    cm_username = module.params.get('cm_username')
    cm_password = module.params.get('cm_password')
    cm_config_key = module.params.get('name')
    cm_config_value = module.params.get('value', None)
    action = module.params.get('action')
    view = module.params.get('view')

    response = dict(changed=False,
                    status_code=0,
                    msg="",
                    content=dict())
    h = httplib2.Http()
    h.add_credentials(cm_username, cm_password)
    resp, respb = h.request(uri=cm_url + '/api/version', method='GET')
    _return_error(resp, respb)
    cm_version = respb.decode('ascii')

    if action == "get":
        resp, respb = h.request(uri=cm_url + '/api/' + cm_version + '/cm/config?view=%s' % view, method='GET')
        _return_error(resp, respb)
        response['status_code'] = resp.status
        cm_config = json.loads(respb.decode('ascii'))
        if cm_config_key:
            config_keys = cm_config_key.split(',')
            response['content'] = dict(items=[item for item in cm_config['items']
                                              if item['name'] in config_keys])
        else:
            response['content'] = cm_config
    elif action == 'set':
        data = {"items": [dict(name=cm_config_key, value=cm_config_value)]}
        resp, respb = h.request(uri=cm_url + '/api/' + cm_version + '/cm/config', method='PUT',
                                headers={'Content-Type': 'Application/json'}, body=json.dumps(data))
        _return_error(resp, respb.decode('ascii'))
        response['status_code'] = resp.status
        response['msg'] = respb.decode('ascii')
    elif action == "delete":
        config_keys = cm_config_key.split(',')
        data = {"items": [dict(name=key, value=None) for key in config_keys]}
        resp, respb = h.request(uri=cm_url + '/api/' + cm_version + '/cm/config', method='PUT',
                                headers={'Content-Type': 'Application/json'}, body=json.dumps(data))
        _return_error(resp, respb.decode('ascii'))
        response['status_code'] = resp.status
        response['msg'] = respb.decode('ascii')

    module.exit_json(**response)


if __name__ == "__main__":
    main()
