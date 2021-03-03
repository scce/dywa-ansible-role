#!/bin/bash

vagrant up

ansible-playbook -i inventory test-local.yml
