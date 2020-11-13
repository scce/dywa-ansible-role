# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enable servers to restore and test backups (#[83](https://github.com/scce/dywa-ansible-role/issues/83))
- Introduce feature to extend Docker image for dywa app (#[78](https://github.com/scce/dywa-ansible-role/issues/78))
- Set timeout of nginx and wildfly via variable (#[85](https://github.com/scce/dywa-ansible-role/issues/85))

### Changed
- Install nginx as a native os package to avoid a bug in docker swarm ([#70](https://github.com/scce/dywa-ansible-role/issues/70))
- Use exposed ports for docker services below 8000 ([#81](https://github.com/scce/dywa-ansible-role/issues/81))
- Use https 443 port for dywa-app ([#73](https://github.com/scce/dywa-ansible-role/issues/73))

### Fixed
- Change ownerships of dywa-app to deploy user ([#75](https://github.com/scce/dywa-ansible-role/issues/75))

## [3.0.0]

### Added
- Add --native parameter to app.sh ([#59](https://github.com/scce/dywa-ansible-role/issues/59))
- Add --remove to app.sh for testing environments ([#54](https://github.com/scce/dywa-ansible-role/issues/54))
- Add user to docker group ([#31](https://github.com/scce/dywa-ansible-role/issues/31))
- Automating Renewals and Hooks ([#32](https://github.com/scce/dywa-ansible-role/issues/32))
- Create robots.txt for all environments except production ([#55](https://github.com/scce/dywa-ansible-role/issues/55))
- Enable HTTP2 between Nginx and Wildfly ([#26](https://github.com/scce/dywa-ansible-role/issues/26))
- Enable HTTP2 for Nginx proxy ([#44](https://github.com/scce/dywa-ansible-role/issues/44))
- Enforce the updating of snapshot-versions ([#58](https://github.com/scce/dywa-ansible-role/issues/58))
- Include wildfly standalone.conf ([#66](https://github.com/scce/dywa-ansible-role/issues/66))
- Introduce error handling in app.sh ([#51](https://github.com/scce/dywa-ansible-role/issues/51))
- Manage ssh authorized keys for deploy user ([#68](https://github.com/scce/dywa-ansible-role/issues/68))
- Migrate backup/restore script ([#50](https://github.com/scce/dywa-ansible-role/issues/50))
- Pinpoint nginx server version for docker images ([#47](https://github.com/scce/dywa-ansible-role/issues/47))
- Re-Establish Maintenance Page ([#64](https://github.com/scce/dywa-ansible-role/issues/64))
- Reintroduce allow_access_address in nginx proxy config ([#56](https://github.com/scce/dywa-ansible-role/issues/56))
- Restart nginx after automated certifiacte renewal ([#13](https://github.com/scce/dywa-ansible-role/issues/13))
- Use deploy user variable for scripts ([#41](https://github.com/scce/dywa-ansible-role/issues/41))
- Using named volume for postgres data directory ([#33](https://github.com/scce/dywa-ansible-role/issues/33))
- Using named volume for wildfly data directory ([#34](https://github.com/scce/dywa-ansible-role/issues/34))

### Changed
- Copy ningx config to conf.d directory ([#38](https://github.com/scce/dywa-ansible-role/issues/38))
- Improve nginx frontend cache ([#43](https://github.com/scce/dywa-ansible-role/issues/43))
- Increase proxy timeout for testing environments ([#53](https://github.com/scce/dywa-ansible-role/issues/53))
- Merge scripts into one single script ([#42](https://github.com/scce/dywa-ansible-role/issues/42))
- Use keepalive connections between nginx proxy and services ([#46](https://github.com/scce/dywa-ansible-role/issues/46))
- dywa-app: Simplify Dockerfile ([#62](https://github.com/scce/dywa-ansible-role/issues/62))

### Removed
- Generate nginx configs and remove docker image dywa-nginx ([#30](https://github.com/scce/dywa-ansible-role/issues/30))

### Fixed
- Access on http without a slash does not redirect properly ([#52](https://github.com/scce/dywa-ansible-role/issues/52))
- Investigate Nginx warning: duplicate MIME type "text/html" ([#40](https://github.com/scce/dywa-ansible-role/issues/40))
- Nginx does not start if upstream servers are not there ([#45](https://github.com/scce/dywa-ansible-role/issues/45))
- Python-based app script misses remove command ([#61](https://github.com/scce/dywa-ansible-role/issues/61))
- Review automated role testing ([#12](https://github.com/scce/dywa-ansible-role/issues/12))
- app.py: Wrong argument name ([#60](https://github.com/scce/dywa-ansible-role/issues/60))

### Security
- Reading database credentials from variables ([#36](https://github.com/scce/dywa-ansible-role/issues/36))
- Reduce amount of using become for unnecessary privilege escalation ([#35](https://github.com/scce/dywa-ansible-role/issues/35))
- Resolve different permissions and ownership between ansible-role and deployment ([#29](https://github.com/scce/dywa-ansible-role/issues/29))
- Secure dywa and mailcatcher paths ([#39](https://github.com/scce/dywa-ansible-role/issues/39))

[unreleased]: https://github.com/scce/dywa-ansible-role/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/scce/dywa-ansible-role/compare/v2.0.0...v3.0.0
