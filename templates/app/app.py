#!/usr/bin/env python3

import argparse
import subprocess


class Runner(object):
    """
    Class for execute the actual commands
    """
    docker_path = '{{ bin_docker }}'
    sudo_path = '{{ bin_sudo }}'
    deploy_user = '{{ deploy_user }}'
    app_root = '{{ app_root }}'
    dywa_database_host = '{{ dywa_database_host }}'
    dywa_database_user = '{{ dywa_database_user }}'
    dywa_database_password = '{{ dywa_database_password }}'

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

    def init(self):
        self.__docker_stack(['deploy', '--compose-file', 'docker-compose.yml', 'app'])

    def build(self):
        self.__docker(['pull', 'scce/dywa:latest'])
        self.__docker_build(tag='scce/webapp', dockerfile='src/Dockerfile-webapp')
        self.__docker_build(tag='scce/dywa-app', dockerfile='src/Dockerfile-dywa-app')
        self.__docker_build(tag='scce/maintenance-page', dockerfile='src/Dockerfile-maintenance-page')

    def migrate(self, native):
        self.__docker_service(['scale', 'app_dywa-app=0'])
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
        self.__subprocess(
            [
                self.sudo_path,
                'chown',
                '-R',
                '%s:%s' % (self.deploy_user, self.deploy_user),
                "%s/maven/repository" % self.app_root
            ]
        )

    def deploy(self, native):
        self.migrate(native)
        self.build()
        self.restart()

    def restart(self):
        services = ['app_webapp', 'app_dywa-app', 'app_nginx']
        for service in services:
            self.__docker_service(['scale', '%s=1' % service])
            self.__docker_service_update(['--force', service])

    def maintenance(self, mode):
        if mode == 'off':
            self.__docker_service_update_image(['scce/webapp', 'app_webapp'])
        else:
            self.__docker_service_update_image(['scce/maintenance-page', 'app_webapp'])

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
        self.create_init_parser(subparsers)
        self.create_migrate_parser(subparsers)
        self.create_build_parser(subparsers)
        self.create_deploy_parser(subparsers)
        self.create_restart_parser(subparsers)
        self.create_maintenance_parser(subparsers)
        self.create_remove_parser(subparsers)
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
            name="init",
            help='Initialize the app stack before you start deploying'
        )
        init_parser.set_defaults(func=self.init)

    def create_migrate_parser(self, subparsers):
        migrate_parser = subparsers.add_parser(
            name="migrate",
            help='Migrate dywa database schema',
        )
        migrate_parser.add_argument(
            '--native',
            action='store_true',
            help='Use native database schema'
        )
        migrate_parser.set_defaults(func=self.migrate)

    def create_build_parser(self, subparsers):
        build_parser = subparsers.add_parser(
            name="build",
            help='Pull latest dywa image and build webapp and dywa-app'
        )
        build_parser.set_defaults(func=self.build)

    def create_deploy_parser(self, subparsers):
        deploy_parser = subparsers.add_parser(
            name="deploy",
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
            name="restart",
            help='Restart webapp, dywa-app and nginx'
        )
        restart_parser.set_defaults(func=self.restart)

    def create_maintenance_parser(self, subparsers):
        restart_parser = subparsers.add_parser(
            name="maintenance",
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
            name="remove",
            help='Remove the app and persisted data'
        )
        remove_parser.set_defaults(func=self.remove)

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

    def migrate(self):
        """
        Migrate dywa database schema
        """
        self.runner.migrate(self.args.native)

    def build(self):
        """
        Deploy webapp and dywa-app by running build, migrate, restart
        """
        self.runner.build()

    def deploy(self):
        """
        Pull latest dywa image and build webapp and dywa-app
        """
        self.runner.deploy(self.args.native)

    def restart(self):
        """
        Restart webapp, dywa-app and nginx
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


if __name__ == '__main__':
    App()
