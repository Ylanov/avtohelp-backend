"""Initial for settings app."""
import os

configuration = os.environ.get('SETTINGS_CONFIGURATION', None)

if configuration == 'local':
    # local machine server settings
    from .local import *
# elif configuration == 'ci':
#     # continious integration server settings
#     from .ci import *
# elif configuration == 'development':
#     # development server settings
#     from .development import *
# elif configuration == 'stage':
#     # development server settings
#     from .stage import *
# elif configuration == 'production':
#     # production server settings
#     from .production import *
else:
    from .base import *
