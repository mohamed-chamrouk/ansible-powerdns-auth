#!/bin/bash

#ansible-playbook -i localhost, workflow-support/ansible-"${1}"/test-tsigkey.yml
#ansible-playbook -i localhost, workflow-support/ansible-"${1}"/test-zone.yml
#ansible-playbook -i localhost, workflow-support/ansible-"${1}"/test-zone-issue-136.yml
#ansible-playbook -i localhost, workflow-support/ansible-"${1}"/test-zone-rrset.yml
#ansible-playbook -i localhost, workflow-support/ansible-2.19/test-rrset-record.yml
ansible-playbook -i localhost, workflow-support/ansible-2.19/test-cryptokey.yml
