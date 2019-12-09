# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add --native parameter to app.sh (#59)
- Add --remove to app.sh for testing environments (#54)
- Add user to docker group (#31)
- Automating Renewals and Hooks (#32)
- Create robots.txt for all environments except production (#55)
- Enable HTTP2 between Nginx and Wildfly (#26)
- Enable HTTP2 for Nginx proxy (#44)
- Enforce the updating of snapshot-versions (#58)
- Include wildfly standalone.conf (#66)
- Introduce error handling in app.sh (#51)
- Manage ssh authorized keys for deploy user (#68)
- Migrate backup/restore script (#50)
- Pinpoint nginx server version for docker images (#47)
- Re-Establish Maintenance Page (#64)
- Reintroduce allow_access_address in nginx proxy config (#56)
- Restart nginx after automated certifiacte renewal (#13)
- Use deploy user variable for scripts (#41)
- Using named volume for postgres data directory (#33)
- Using named volume for wildfly data directory (#34)

### Changed
- Copy ningx config to conf.d directory (#38)
- Improve nginx frontend cache (#43)
- Increase proxy timeout for testing environments (#53)
- Merge scripts into one single script (#42)
- Use keepalive connections between nginx proxy and services (#46)
- dywa-app: Simplify Dockerfile (#62)

### Removed
- Generate nginx configs and remove docker image dywa-nginx (#30)

### Fixed
- Access on http without a slash does not redirect properly (#52)
- Investigate Nginx warning: duplicate MIME type "text/html" (#40)
- Nginx does not start if upstream servers are not there (#45)
- Python-based app script misses remove command (#61)
- Review automated role testing (#12)
- app.py: Wrong argument name (#60)

### Security
- Reading database credentials from variables (#36)
- Reduce amount of using become for unnecessary privilege escalation (#35)
- Resolve different permissions and ownership between ansible-role and deployment (#29)
- Secure dywa and mailcatcher paths (#39)

[unreleased]: https://github.com/scce/dywa-ansible-role/compare/v2.0.0...HEAD
