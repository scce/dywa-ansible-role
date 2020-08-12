# SCCE / DyWA Ansible Role [![Build Status](https://api.travis-ci.org/scce/dywa-ansible-role.svg?branch=master)](https://travis-ci.org/sce/dywa-ansible-role)

Ansible role which installs and configures DyWA with PostgreSQL as database backend and Nginx as proxy.

## Installation

This has been tested on Ansible 2.4.0 and higher.

To install:

```
ansible-galaxy install scce.dywa
```

## Example Playbook

Including an example of how to use your role:

    - hosts: all
      roles:
         - { role: scce.dywa }

## Variables

```yaml
    backup_enabled: True
    backup_remote_host: localhost
    backup_user_id_rsa_path: files/id_rsa
    certbot_email: john.doe@example.org
    deploy_user: john.doe
    deploy_user_authorized_keys: []
    deployment_tier: testing
    domain: example.org
    dywa_database_password: password
    dywa_database_user: user
    dywa_dockerfile_add_on: 'RUN yum install -y texlive-pdftex-bin'
    dywa_http_auth_password: user
    dywa_http_auth_username: password
    mailcatcher_http_auth_password: user
    mailcatcher_http_auth_username: password
    maven_edu_password: user
    maven_edu_username: password
    restic_repo_url: /tmp/restic
    restic_repository_password: password
    restore_enabled: True
```

## License

Licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
