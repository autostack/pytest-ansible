pytest-ansible
==============

Pytest plugin for integrating with Ansible


Getting Started
---------------

### Installation
* Use virtual environment wrapper [Install virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)
* Install and start redis serer instance
```
# yum install redist-server
# redis-server &
```
* Clone pytest-ansible and create virtual env
```
# git clone https://github.com/autostack/pytest-ansible.git
# mkvirtualenv autostack
```
* Update inventory1.yaml with you setup IPs
  * Make sure you have passwordless ssh connections to those machines
  * Update "ansible_ssh_user" with the user you login, in case of "root" remove "ansible_sudo"
