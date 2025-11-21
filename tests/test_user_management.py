import pytest
import requests
from faker import Faker
import allure
from tests.urls import Urls


@allure.epic("User Management")
@allure.feature("User Registration")
class TestUserCreation:

    @allure.title("Create a unique user successfully")
    @allure.description("Test case for creating a unique user.")
    def test_create_unique_user_success(self, generate_user_data):
        payload = generate_user_data
        response = requests.post(f'{Urls.MAIN_URL}/api/auth/register', data=payload)
        
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.json()["success"] is True, "Expected 'success' to be True"
        
        access_token = response.json().get("accessToken")
        assert access_token is not None, "Access token was not found in the response"

        headers = {"Authorization": access_token}
        delete_response = requests.delete(f'{Urls.MAIN_URL}/api/auth/user', headers=headers)
        assert delete_response.status_code == 202, "User cleanup failed"

    @allure.title("Create a user that is already registered")
    @allure.description("Test case for creating a user that already exists.")
    def test_create_duplicate_user_error(self, register_user):
        user_payload, _ = register_user
        response = requests.post(f'{Urls.MAIN_URL}/api/auth/register', data=user_payload)
        
        assert response.status_code == 403
        assert response.json()["success"] is False
        assert response.json()["message"] == "User already exists"

    @allure.title("Create a user without a required field")
    @allure.description("Test case for creating a user without one of the required fields.")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_missing_field_error(self, missing_field, generate_user_data):
        payload = generate_user_data
        del payload[missing_field]
        
        response = requests.post(f'{Urls.MAIN_URL}/api/auth/register', data=payload)
        
        assert response.status_code == 403
        assert response.json()["success"] is False
        assert response.json()["message"] == "Email, password and name are required fields"


@allure.epic("User Management")
@allure.feature("User Login")
class TestUserLogin:

    @allure.title("Login with an existing user")
    @allure.description("Test case for logging in with a valid, existing user.")
    def test_login_existing_user_success(self, register_user):
        user_payload, _ = register_user
        login_payload = {
            "email": user_payload["email"],
            "password": user_payload["password"]
        }
        response = requests.post(f'{Urls.MAIN_URL}/api/auth/login', data=login_payload)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "accessToken" in response.json()

    @allure.title("Login with incorrect credentials")
    @allure.description("Test case for logging in with an incorrect email and password.")
    def test_login_incorrect_credentials_error(self):
        fake = Faker()
        payload = {
            "email": fake.email(),
            "password": fake.password(length=10)
        }
        response = requests.post(f'{Urls.MAIN_URL}/api/auth/login', data=payload)
        
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "email or password are incorrect"


@allure.epic("User Management")
@allure.feature("Update User Data")
class TestUpdateUserData:

    @allure.title("Update user data with authorization")
    @allure.description("Test case for updating user's name and email with authorization.")
    def test_update_user_with_auth_success(self, register_user):
        _, access_token = register_user
        fake = Faker()
        new_data = {
            "name": fake.first_name(),
            "email": fake.email()
        }
        headers = {"Authorization": access_token}
        
        response = requests.patch(f'{Urls.MAIN_URL}/api/auth/user', headers=headers, data=new_data)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["user"]["name"] == new_data["name"]
        assert response.json()["user"]["email"] == new_data["email"]

    @allure.title("Update user data without authorization")
    @allure.description("Test case for attempting to update user data without authorization.")
    def test_update_user_without_auth_error(self, generate_user_data):
        new_data = {
            "name": generate_user_data["name"],
            "email": generate_user_data["email"]
        }
        
        response = requests.patch(f'{Urls.MAIN_URL}/api/auth/user', data=new_data)
        
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "You should be authorised"
