import imp
import sys
import time
import os.path
import traceback

from migrate.versioning import api

from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

from app.models import Role, Setting, DomainTemplate, User
from app import db, script_manager


@script_manager.command
def db_downgrade():
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' + str(v))


@script_manager.command
def db_migrate():
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    exec(old_model, tmp_module.__dict__)
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ' + migration)
    print('Current database version: ' + str(v))


@script_manager.command
def db_upgrade():
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' + str(v))


@script_manager.command
def create_db():
    wait_time = int(os.environ.get('WAITFOR_DB', 1))
    if not connect_db(wait_time):
        print("ERROR: Couldn't connect to database server")
        exit(1)
    init_records()


@script_manager.command
def create_admin(username, plain_text_password):
    admin = User(username=username, plain_text_password=plain_text_password, role_id=1)
    print(admin.create_local_user())


def connect_db(wait_time):
    for i in range(0, wait_time):
        print("INFO: Wait for database server")
        sys.stdout.flush()
        try:
            db.create_all()
            return True
        except:
            traceback.print_exc()
            time.sleep(1)

    return False


def init_roles(db, role_names):
    # Get key name of data
    name_of_roles = [r.name for r in role_names]
    # Query to get current data
    rows = db.session.query(Role).filter(Role.name.in_(name_of_roles)).all()
    name_of_rows = [r.name for r in rows]
    # Check which data that need to insert
    roles = [r for r in role_names if r.name not in name_of_rows]
    # Insert data
    for role in roles:
        db.session.add(role)


def init_settings(db, setting_names):
    # Get key name of data
    name_of_settings = [r.name for r in setting_names]
    # Query to get current data
    rows = db.session.query(Setting).filter(Setting.name.in_(name_of_settings)).all()
    # Check which data that need to insert
    name_of_rows = [r.name for r in rows]
    settings = [r for r in setting_names if r.name not in name_of_rows]
    # Insert data
    for setting in settings:
        db.session.add(setting)


def init_domain_templates(db, domain_template_names):
    # Get key name of data
    name_of_domain_templates = map(lambda r: r.name, domain_template_names)
    # Query to get current data
    rows = db.session.query(DomainTemplate).filter(DomainTemplate.name.in_(name_of_domain_templates)).all()
    # Check which data that need to insert
    name_of_rows = map(lambda r: r.name, rows)
    domain_templates = filter(lambda r: r.name not in name_of_rows, domain_template_names)
    # Insert data
    for domain_template in domain_templates:
        db.session.add(domain_template)


def init_records():
    # Create initial user roles and turn off maintenance mode
    init_roles(db, [
        Role('Administrator', 'Administrator'),
        Role('User', 'User')
    ])
    init_settings(db, [
        Setting('maintenance', 'False'),
        Setting('fullscreen_layout', 'True'),
        Setting('record_helper', 'True'),
        Setting('login_ldap_first', 'True'),
        Setting('default_record_table_size', '15'),
        Setting('default_domain_table_size', '10'),
        Setting('auto_ptr','False')
    ])
    # TODO: add sample records to sample templates
    init_domain_templates(db, [
        DomainTemplate('basic_template_1', 'Basic Template #1'),
        DomainTemplate('basic_template_2', 'Basic Template #2'),
        DomainTemplate('basic_template_3', 'Basic Template #3')
    ])
    db_commit = db.session.commit()
    commit_version_control(db_commit)


def commit_version_control(db_commit):
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    elif db_commit is not None:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))


if __name__ == "__main__":
    script_manager.run()

