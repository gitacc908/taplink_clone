import environ
env = environ.Env()


SECRET_KEY = env.str('DJANGO_SECRET_KEY', default='not secret)')

DEBUG = env.bool('DJANGO_DEBUG', default=True)

DATABASES = {
    'default': env.db(
        'DATABASE_URL', default='sqlite:///db.sqlite'
    )
}

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])
