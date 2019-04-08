"""Initial for settings app."""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Common path section
PUBLIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'media'))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

CONFIG_FILE = f'{PROJECT_ROOT}/roadhelper.ini'
if os.path.exists(CONFIG_FILE):
    for i in open(CONFIG_FILE):
        key, value = i.rstrip().split('=')
        os.environ[key] = value

configuration = os.environ.get('SETTINGS_CONFIGURATION', None)

if configuration == 'local':
    # local machine server settings
    from .local import *
# elif configuration == 'ci':
#     # continious integration server settings
#     from .ci import *
elif configuration == 'development':
    # development server settings
    from .development import *
# elif configuration == 'stage':
#     # development server settings
#     from .stage import *
# elif configuration == 'production':
#     # production server settings
#     from .production import *
else:
    from .base import *
