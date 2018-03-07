# Ansible customized modules

This repository holds many customized modules to use in Ansible, they provide functions that are not found in Ansible offcial modules.


## Repository structure

The structure of this repository takes form of [Ansible directory layout](http://docs.ansible.com/ansible/latest/playbooks_best_practices.html#directory-layout)

 - library: contains customized modules which can be called directly from playbook
 - module_utils: contains scripts / python modules that used by customized modules
 - filter_plugins: customized filter which can be used directly in playbook

The customized modules are independent, each stored in its own folder with its README and test. Each and every file is a standalone module and can be downloaded and called in any playbook.


## How to use a customized module

To use a module, simply download the .py module file and put into `library` folder in your playbook directory. Note that some modules may need some python modules from module_utils, which need to be downloaded a long with the module itself and saved in `module_utils` folder. The README file of the module specifies which standard python libraries and which module_utils needed.
