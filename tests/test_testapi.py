import pytest

from adsapi import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
