import pytest
import redis

from django.conf import settings
from django.contrib.auth import get_user_model
from smart.celery import app as celery_app
from core.management.commands.seed import (
    seed_database, SEED_USERNAME)
from core.models import (Profile)
from core.util import (create_project, add_queue,
                       create_profile, add_data)

from test.util import read_test_data

TEST_QUEUE_LEN = 10

@pytest.fixture()
def seeded_database(db):
    # Seed the database using the management command
    seed_database()

@pytest.fixture(autouse=True)
def setup_celery():
    celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

@pytest.fixture(scope='function')
def test_redis(request):
    r = settings.REDIS

    # Teardown by removing all keys when we're done with the fixture
    def teardown():
        r.flushdb()
    request.addfinalizer(teardown)

    return r

@pytest.fixture
def test_project(db):
    '''
    This fixture only creates the test project without any data.
    '''
    return create_project('test_project')

@pytest.fixture
def test_project_data(db, test_project):
    '''
    Creates the test project and adds test data to it.
    '''
    test_data = read_test_data()
    add_data(test_project, test_data)
    return test_project

@pytest.fixture
def test_profile(db):
    '''
    Creates a test profile with associated auth_user.
    '''
    return create_profile('test_profile', 'password', 'test_profile@rti.org')

@pytest.fixture
def test_profile2(db):
    '''
    Additional profile for tests requiring multiple users.
    '''
    return create_profile('test_profile2', 'password', 'test_profile2@rti.org')

@pytest.fixture
def test_queue(db, test_project_data):
    '''
    A queue containing data from the test project, with length set to
    the global len.
    '''
    return add_queue(test_project_data, TEST_QUEUE_LEN)

@pytest.fixture
def test_profile_queue(db, test_profile, test_project_data):
    '''
    A queue with test data, associated with the first test profile.
    '''
    return add_queue(test_project_data, TEST_QUEUE_LEN, profile=test_profile)

@pytest.fixture
def test_profile_queue2(db, test_profile2, test_project_data):
    '''
    A queue with test data, associated with an additional test profile.
    Useful for tests requiring multiple profiles/queues on the same project.
    '''
    return add_queue(test_project_data, TEST_QUEUE_LEN, profile=test_profile2)
