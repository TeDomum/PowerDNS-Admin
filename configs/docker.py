import os
basedir = os.path.abspath(os.path.dirname(__file__))

# base configuration
WTF_CSRF_ENABLED = True
SECRET_KEY = os.urandom(32)
LOG_LEVEL = 'INFO'
LOG_FILE = '/data/main.log'
TIMEOUT = 10
UPLOAD_DIR = '/data/uploads/'

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:////data/pdnsadmin.sqlite'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Authentication
BASIC_ENABLED = True
SIGNUP_ENABLED = False
SAML_ENABLED = False
LDAP_ENABLED = False

# Server config
PDNS_STATS_URL = 'http://{0}:8081'.format(os.environ.get('PDNS_HOST'))
PDNS_API_KEY = os.environ.get('PDNS_API_KEY')
PDNS_VERSION = '4.1.1'

# Records
RECORDS_ALLOW_EDIT = ['SOA', 'A', 'AAAA', 'CAA', 'CNAME', 'MX', 'PTR', 'SPF', 'SRV', 'TXT', 'LOC', 'NS', 'PTR']
FORWARD_RECORDS_ALLOW_EDIT = ['A', 'AAAA', 'CAA', 'CNAME', 'MX', 'PTR', 'SPF', 'SRV', 'TXT', 'LOC' 'NS']
REVERSE_RECORDS_ALLOW_EDIT = ['SOA', 'TXT', 'LOC', 'NS', 'PTR']

# Experimental
PRETTY_IPV6_PTR = True

# Update config using Docker options
import json
for name in globals().copy():
    env = "PDNS_{}".format(name)
    if env in os.environ:
        try:
            value = json.loads(os.environ[env])
        except:
            value = os.environ[env]
        finally:
            print("{} = {}".format(name, repr(value)))
            globals()[name] = value

