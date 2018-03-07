# Cloudera Manager Configuration module

This module is used for getting/setting/deleting Cloudera Manager configuration.


## Usage

Put this python file in `library` folder under the playbook folder, it can be called directly from the playbooks.

| parameter | required | default| choices | comments |
|--------------|----------|----------|----------|----|
| cm_url | yes | | | URL for Cloudera Manager |
| cm_username | yes | | | User for Cloudera Manager |
| cm_password | yes | | | Password for Cloudera Manager |
| name | no | None | | Configuration item to change. Required if `action` is `set` or `delete`. If `action` is `get` or `delete`, name can be a colon-separated string. If `action` is `get` and `name` is not present (Null), will get all configuration; this will be a lot. |
| value | no | | | Value of the configuration, only required when `action` is `set` |
| action | yes | | get / set / delete | Action to take |
| view | no | summary | summary / full | Only used when `action` is `get`. `summary` will get only modified configurations with limited information. `full` will return all configuration with all information. |


## Requirements

 - This module requires httplib2 Python library installed on remote host.


## Compatibility

Compatible Python2, Python3.


## Notes:

 - In case of `get` `action`, if `name` is not in Cloudera Manager configuration list, the module simply returns empty value (Null). It will not be considered as error.

 - When `view` is `summary`, the module will only return modified configuration items, thus the results may not contain all requested items from `name`. `full` `view` will.


## Examples

```yml
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
 ```


## Questions

 1. Why not using cm-api ?

Although cm-api is natural choice for interacting Cloudera Manger, at this moment (Mars 2018) it does not work with Python 3 thanks to usage of urllib2. Thus it will not work on Python3-shipped OS such as Ubuntu 16.04.
