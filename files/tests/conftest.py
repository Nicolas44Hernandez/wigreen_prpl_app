import pytest
from unittest.mock import patch


@pytest.fixture
def mock_sleep():
    with patch("time.sleep", return_value=None) as mock:
        yield mock  # Provide the mock to the test
