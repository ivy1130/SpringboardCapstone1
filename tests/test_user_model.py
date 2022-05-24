"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///cat_finder_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test model for User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.commit()

        self.u1 = u1
        self.uid1 = u1.id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown() 
        db.session.rollback()
        return res

    def test_user_model(self):
        """The User model works."""

        u = self.u1
        # User should have no favorites.
        self.assertEqual(len(u.favorites), 0)
        self.assertEqual(u.username, 'testuser1')
        self.assertEqual(u.email, 'test1@test.com')
    
    def test_user_model_repr(self):
        """The User model repr is correct."""

        u = self.u1

        self.assertEqual(str(u), f"<User #{self.uid1}: testuser1, test1@test.com>")
    
    def test_user_model_sign_up_success(self):
        """The signup method successully creates a new user."""
        u = User.signup(
            username="testuser",
            password="HASHED_PASSWORD",
            email="test@test.com",
            image_url=None
        )
        db.session.commit()

        self.assertEqual(len(u.favorites), 0)
        self.assertEqual(u.image_url, "https://icon-library.com/images/anonymous-person-icon/anonymous-person-icon-18.jpg")
        self.assertTrue(u.password.startswith("$2b$"))
    
    def test_user_model_sign_up_username_fail(self):
        """The signup method fails when it's missing required inputs."""
        u = User.signup(
            username=None,
            password="HASHED_PASSWORD",
            email="test@test.com",
            image_url=None
        )
       
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_model_sign_up_password_fail(self):
        """The signup method fails when it's missing required inputs."""
        with self.assertRaises(ValueError) as context:
            u = User.signup(
                username="testuser",
                password=None,
                email="test@test.com",
                image_url=None
            )
    
    def test_valid_authentication(self):
        """The authenticate method successully authenticates a valid user and password."""
        u = User.authenticate("testuser1", "HASHED_PASSWORD")
        self.assertIsNotNone(u)
        self.assertEqual(u, self.u1)
    
    def test_invalid_username(self):
        """The authenticate method fails when the username is invalid."""
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_wrong_password(self):
        """The authenticate method fails when the password is invalid."""
        self.assertFalse(User.authenticate("testuser1", "invalidpassword"))


