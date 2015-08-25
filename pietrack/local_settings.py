DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'pietrack',
        'USER':     'root',
        'PASSWORD': 'root',
        'HOST':     'localhost',
        'PORT':     '3306',
    }
}

EMAIL_HOST_USER = 'your_email'
EMAIL_HOST_PASSWORD = 'your_password'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
