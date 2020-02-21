#!/usr/bin/env python3

import argparse
import subprocess


class Runner(object):
    """
    Class for execute the actual commands
    """
    app_root = '{{ app_root }}'
    deploy_user = '{{ deploy_user }}'
    docker_path = '{{ bin_docker }}'
    dywa_database_host = '{{ dywa_database_host }}'
    dywa_database_password = '{{ dywa_database_password }}'
    dywa_database_user = '{{ dywa_database_user }}'
    restic_repo_url = '{{ restic_repo_url }}'
    sudo_path = '{{ bin_sudo }}'

    @staticmethod
    def __subprocess(commands):
        subprocess.run(commands).check_returncode()

    def __docker(self, commands):
        Runner.__subprocess([self.docker_path] + commands)

    def __docker_build(self, tag, dockerfile):
        self.__docker(['build', '-t', tag, '-f', dockerfile, 'src'])

    def __docker_service(self, commands):
        self.__docker(['service'] + commands)

    def __docker_service_update(self, commands):
        self.__docker_service(['update'] + commands)

    def __docker_service_update_image(self, commands):
        self.__docker_service_update(['--image'] + commands)

    def __docker_stack(self, commands):
        self.__docker(['stack'] + commands)

    def __docker_scale(self, commands):
        self.__docker_service(['scale'] + commands)

    def __build_maintenance_page(self):
        self.__docker_build(tag='scce/maintenance-page', dockerfile='src/Dockerfile-maintenance-page')

    def __update_service(self, service):
        self.__docker_service_update(['--force', service])

    def __stop_dywa_app(self):
        self.__docker_scale(['app_dywa-app=0'])

    def __start_dywa_app(self):
        self.__docker_scale(['app_dywa-app=1'])

    def __start_webapp(self):
        self.__docker_scale(['app_webapp=1'])

    def __maintenance_mode_off(self):
        self.maintenance(mode='off')

    def __maintenance_mode_on(self):
        self.maintenance(mode='on')

    def __update_dywa_app_and_webapp(self):
        self.__update_service('app_dywa-app')
        self.__update_service('app_webapp')

    def __migrate(self, native):
        self.__docker(
            [
                'run',
                '--rm',
                '--network=app_postgres',
                '-v=%s/maven/:/root/.m2' % self.app_root,
                '-v=%s/src/dywa-app:/usr/src/mymaven' % self.app_root,
                '-w=/usr/src/mymaven/app-dywa-bridge',
                'maven:3.5.4',
                'mvn',
                '-U',
                'package',
                '-Dde.ls5.dywa.jdbc-connection-url=jdbc:postgresql://%s:5432/dywa' % self.dywa_database_host,
                '-Dde.ls5.dywa.jdbc-user=%s' % self.dywa_database_user,
                '-Dde.ls5.dywa.jdbc-password=%s' % self.dywa_database_password,
                '-Dhibernate.dialect=org.hibernate.dialect.PostgreSQLDialect',
                '-Ddime.native=%s' % ('%s' % native).lower()
            ]
        )
        # the migration container writes as root, so we have to fix the ownerships
        self.__subprocess(
            [
                self.sudo_path,
                'chown',
                '-R',
                '%s:%s' % (self.deploy_user, self.deploy_user),
                "%s/maven/repository" % self.app_root,
                "%s/src/dywa-app" % self.app_root,
            ]
        )

    def __backup(self, command, arguments=None):
        if arguments is None:
            arguments = []
        self.__docker(
            [
                'run',
                '--network=app_postgres',
                '--rm',
                '-e=ENV_RESTIC_REPO_URL=%s' % self.restic_repo_url,
                '-e=PGDATABASE=dywa',
                '-e=PGHOST=%s' % self.dywa_database_host,
                '-e=PGPASSWORD=%s' % self.dywa_database_password,
                '-e=PGUSER=%s' % self.dywa_database_user,
                '-v=%s/config/backup/id_rsa:/root/.ssh/id_rsa:ro' % self.app_root,
                '-v=%s/config/backup/restic-repository-password:/root/.repository-password:ro' % self.app_root,
                '-v=%s/config/backup/ssh_config:/etc/ssh/ssh_config:ro' % self.app_root,
                '-v=app_wildfly:/opt/jboss/wildfly/standalone/data/files',
                '-v=restic-cache:/root/.cache/restic',
                'scce/dywa-backup',
                '--%s' % command
            ] + arguments
        )

    def init(self):
        self.__docker_stack(['deploy', '--compose-file', 'docker-compose.yml', 'app'])
        # build maintenance page so that we can use the maintenance page during initial deployment
        self.__build_maintenance_page()

    def build(self):
        self.__docker(['pull', 'scce/dywa:latest'])
        self.__docker_build(tag='scce/webapp', dockerfile='src/Dockerfile-webapp')
        self.__docker_build(tag='scce/dywa-app', dockerfile='src/Dockerfile-dywa-app')
        self.__build_maintenance_page()

    def backup(self):
        self.__maintenance_mode_on()
        self.__backup(command='backup')
        self.__maintenance_mode_off()

    def snapshots(self):
        self.__backup(command='snapshots')

    def restore(self):
        self.__maintenance_mode_on()
        self.__backup(command='restore', arguments=['latest', '-y'])
        self.__maintenance_mode_off()

    def deploy(self, native):
        self.__maintenance_mode_on()
        self.__migrate(native)
        self.build()
        self.__update_dywa_app_and_webapp()
        self.__maintenance_mode_off()

    def restart(self):
        self.__update_dywa_app_and_webapp()
        self.__start_dywa_app()
        self.__start_webapp()

    def maintenance(self, mode):
        # for the initial deployment we have to make sure that webapp is started
        self.__start_webapp()
        if mode == 'off':
            self.__start_dywa_app()
            self.__docker_service_update_image(['scce/webapp', 'app_webapp'])
        else:
            self.__docker_service_update_image(['scce/maintenance-page', 'app_webapp'])
            self.__stop_dywa_app()

    def remove(self):
        self.__docker_stack(['remove', 'app'])
        self.__docker(['volume', 'rm', 'app_postgres', 'app_wildfly'])


class App(object):
    """
    Class for handling the command line interface
    """
    deployment_tier = '{{ deployment_tier }}'
    runner = Runner()

    def __init__(self):
        parser = self.create_parser()
        args = parser.parse_args()
        self.args = args
        self.execute_command(parser, args)

    def create_parser(self):
        parser = argparse.ArgumentParser(description='Script to control the app deployment')
        subparsers = self.create_subparsers(parser)
        self.create_backup_parser(subparsers)
        self.create_build_parser(subparsers)
        self.create_deploy_parser(subparsers)
        self.create_init_parser(subparsers)
        self.create_maintenance_parser(subparsers)
        self.create_remove_parser(subparsers)
        self.create_restart_parser(subparsers)
        self.create_restore_parser(subparsers)
        self.create_snapshots_parser(subparsers)
        return parser

    @staticmethod
    def create_subparsers(parser):
        subparsers = parser.add_subparsers(
            title='Command to run',
            dest='command'
        )
        return subparsers

    def create_init_parser(self, subparsers):
        init_parser = subparsers.add_parser(
            name='init',
            help='Initialize the app stack before you start deploying'
        )
        init_parser.set_defaults(func=self.init)

    def create_build_parser(self, subparsers):
        build_parser = subparsers.add_parser(
            name='build',
            help='Pull latest dywa image and build webapp and dywa-app'
        )
        build_parser.set_defaults(func=self.build)

    def create_backup_parser(self, subparsers):
        build_parser = subparsers.add_parser(
            name='backup',
            help='Perform backup'
        )
        build_parser.set_defaults(func=self.backup)

    def create_restore_parser(self, subparsers):
        build_parser = subparsers.add_parser(
            name='restore',
            help='Perform restore'
        )
        build_parser.set_defaults(func=self.restore)

    def create_deploy_parser(self, subparsers):
        deploy_parser = subparsers.add_parser(
            name='deploy',
            help='Deploy webapp and dywa-app by running build, migrate, restart',
        )
        deploy_parser.add_argument(
            '--native',
            action='store_true',
            help='Use native database schema'
        )
        deploy_parser.set_defaults(func=self.deploy)

    def create_restart_parser(self, subparsers):
        restart_parser = subparsers.add_parser(
            name='restart',
            help='Restart webapp and dywa-app'
        )
        restart_parser.set_defaults(func=self.restart)

    def create_maintenance_parser(self, subparsers):
        restart_parser = subparsers.add_parser(
            name='maintenance',
            help='Manage maintenance mode'
        )
        restart_parser.add_argument(
            'mode',
            type=str,
            help='Mode can be "on" or "off"'
        )
        restart_parser.set_defaults(func=self.maintenance)

    def create_remove_parser(self, subparsers):
        remove_parser = subparsers.add_parser(
            name='remove',
            help='Remove the app and persisted data'
        )
        remove_parser.set_defaults(func=self.remove)

    def create_snapshots_parser(self, subparsers):
        remove_parser = subparsers.add_parser(
            name='snapshots',
            help='Show snapshots in the backup repository'
        )
        remove_parser.set_defaults(func=self.snapshots)

    @staticmethod
    def execute_command(parser, args):
        if not hasattr(args, 'func'):
            parser.print_help()
            exit(1)
        args.func()

    def is_production(self):
        return self.deployment_tier == 'production'

    def init(self):
        """
        Initialize the app stack before you start deploying
        """
        self.runner.init()

    def build(self):
        """
        Deploy webapp and dywa-app by running build, migrate, restart
        """
        self.runner.build()

    def backup(self):
        """
        Perform backup
        """
        self.runner.backup()

    def restore(self):
        """
        Perform restore
        """
        self.runner.restore()

    def deploy(self):
        """
        Pull latest dywa image and build webapp and dywa-app
        """
        self.runner.deploy(self.args.native)

    def restart(self):
        """
        Restart webapp and dywa-app
        """
        self.runner.restart()

    def maintenance(self):
        """
        Manage maintenance mode
        """
        self.runner.maintenance(self.args.mode)

    def remove(self):
        """
        Remove the app and persisted data
        """
        if self.is_production():
            print('Remove not allowed in production')
            exit(1)
        self.runner.remove()

    def snapshots(self):
        """
        Show snapshots in the backup repository
        """
        self.runner.snapshots()


if __name__ == '__main__':
    App()
