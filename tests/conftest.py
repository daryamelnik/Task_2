import pytest
import requests
from faker import Faker
from tests.urls import Urls
import time


@pytest.fixture
def generate_user_data():
    """Generate unique fake user data."""
    fake = Faker()
    timestamp = int(time.time() * 1000)
    return {
        "email": f"test_user_{timestamp}@example.com",
        "password": fake.password(length=10),
        "name": fake.first_name()
    }


@pytest.fixture
def register_user(generate_user_data):
    """Register a new user and clean up after."""
    user_payload = generate_user_data
    response = requests.post(f'{Urls.MAIN_URL}/api/auth/register', data=user_payload)
    
    assert response.status_code == 200, f"Failed to register user. Response: {response.text}"
    assert response.json()["success"] is True, "User registration was not successful"
    
    access_token = response.json().get("accessToken")
    assert access_token is not None, "Access token not found after registration"

    yield user_payload, access_token

    if access_token:
        headers = {"Authorization": access_token}
        requests.delete(f'{Urls.MAIN_URL}/api/auth/user', headers=headers)


@pytest.fixture
def get_ingredient_hashes():
    """Get a list of ingredient hashes."""
    response = requests.get(f'{Urls.MAIN_URL}/api/ingredients')
    assert response.status_code == 200, "Failed to get ingredients"
    ingredients = response.json().get("data")
    assert ingredients is not None, "No ingredients data in response"
    return [ingredient["_id"] for ingredient in ingredients]
