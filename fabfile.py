from fabric.api import *  # NOQA


user = 'roadhelper'

env.roledefs = {
    'develop': {
        'branch': 'develop',
        'hosts': ['%s@rock.spider.ru:31' % user, ]
    },
}


env.root = '~/'
env.src = '~/project'

env.default_branch = 'develop'
env.tmpdir = '~/tmp'


def fetch(branch=None):
    with cd(env.src):
        role = env.roles[0]
        run('git pull origin {}'.format(env.roledefs[role]['branch']))
        run('git submodule update')


def migrate():
    with cd(env.src):
        run('./manage.py migrate')


def install_requirements():
    with cd(env.src):
        run('pip install -r requirements/base.txt')


def touch():
    with cd(env.src):
        run('touch ~/%s.touch' % user)


def kill_celery():
    """Kill celery workers for $user."""
    with cd(env.src):
        run('ps -u %s -o pid,fname | grep celery | (while read a b; do kill -9 $a; done;)' % user)


def collectstatic():
    with cd(env.src):
        run('./manage.py collectstatic --noinput')


def deploy(branch=None):
    fetch()
    install_requirements()
    migrate()
    collectstatic()
    touch()
    kill_celery()


def rev():
    """Show head commit."""
    with hide('running', 'stdout'):
        with cd(env.src):
            commit = run('git rev-parse HEAD')
    return local('git show -q %s' % commit)
