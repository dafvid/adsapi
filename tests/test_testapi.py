import pytest

from testapi import app


@pytest.fixture
def client():
    app.config['TESTING'] = True