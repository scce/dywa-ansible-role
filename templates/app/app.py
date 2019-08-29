#!/usr/bin/env python3

import argparse
import subprocess
import sys


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

    def __docker_stack(self, commands):
        self.__docker(['stack'] + commands)

    def init(self):
        self.__docker_stack(['deploy', '--compose-file', 'docker-compose.yml', 'app'])

    def build(self):
        self.__docker(['pull', 'scce/dywa:latest'])
        self.__docker_build(tag='scce/webapp', dockerfile='src/Dockerfile-webapp')
        self.__docker_build(tag='scce/dywa-app', dockerfile='src/Dockerfile-dywa-app')

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
            self.__docker_service(['update', '--force', service])

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
        parser = argparse.ArgumentParser(
            description='Script to control the app deployment',
            usage='''app <command> [<args>]

These are common App commands used in various situations:
    init         Initialize the app stack before you start deploying
    migrate      Migrate dywa database schema
    build        Pull latest dywa image and build webapp and dywa-app
    deploy       Deploy webapp and dywa-app by running build, migrate, restart
    restart      Restart webapp, dywa-app and nginx
    remove       Remove the app and persisted data
''')
        parser.add_argument('command', help='Command to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    @staticmethod
    def __parse_native_argument():
        parser = argparse.ArgumentParser(
            description='Deploy webapp and dywa-app by running build, migrate, restart'
        )
        parser.add_argument(
            '--native',
            action='store_true',
            help='Use native database schema'
        )
        return parser.parse_args(sys.argv[2:]).native

    def __is_production(self):
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
        native = self.__parse_native_argument()
        self.runner.migrate(native)

    def build(self):
        """
        Deploy webapp and dywa-app by running build, migrate, restart
        """
        self.runner.build()

    def deploy(self):
        """
        Pull latest dywa image and build webapp and dywa-app
        """
        native = self.__parse_native_argument()
        self.runner.deploy(native)

    def restart(self):
        """
        Restart webapp, dywa-app and nginx
        """
        self.runner.restart()

    def remove(self):
        """
        Remove the app and persisted data
        """
        if self.__is_production():
            print('Remove not allowed in production')
            exit(1)
        self.runner.remove()


if __name__ == '__main__':
    App()
