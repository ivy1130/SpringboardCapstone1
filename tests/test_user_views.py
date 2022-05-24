"""User View tests."""

import os
from unittest import TestCase
from models import db, connect_db, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///cat_finder_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()
        Favorite.query.delete()

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url=None
        )

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.commit()

        self.u1 = u1
        self.uid1 = u1.id

        self.u2 = u2
        self.uid2 = u2.id

        f1 = Favorite(
            user_id=self.uid1,
            breed_name="Abyssinian"
        )

        db.session.add(f1)
        db.session.commit()

        self.f1 = f1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_user_success(self):
        """Add new user successfully."""
        with self.client as c:
            d = {"email" : "test3@test.com",
                "username" : "testuser3",
                "password" : "HASHED_PASSWORD",
                "image_url" : ""}
            resp = c.post('/signup', data = d, follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Logout', html)

            resp_profile = c.get('/users/3')
            html_profile = resp_profile.get_data(as_text=True)

            self.assertIn('testuser3', html_profile)
            self.assertIn('https://icon-library.com/images/anonymous-person-icon/anonymous-person-icon-18.jpg', html_profile)

    def test_add_user_fail(self):
        """Add new user failure."""
        with self.client as c:
            d = {"email" : "test1@test.com",
                "username" : "testuser1",
                "password" : "HASHED_PASSWORD",
                "image_url" : ""}
            resp = c.post('/signup', data = d, follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username already taken', html)

    def test_show_user_profile_anon(self):
        """Anonymous users cannot view user profiles."""
        with self.client as c:
            resp = c.get(f'/users/{self.uid1}')

            self.assertEqual(resp.status_code, 302)
            
            resp_redirect = c.get(f'/users/{self.uid1}', follow_redirects=True)
            html = resp_redirect.get_data(as_text=True)

            self.assertEqual(resp_redirect.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_show_user_profile_other(self):
        """Authenticated users can view other user profiles."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid2

        resp = c.get(f'/users/{self.uid1}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("testuser1", html)
        self.assertIn("Abyssinian", html)

    def test_show_user_profile_self(self):
        """Authenticated users can view and have the option to edit and delete their own profile."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

        resp = c.get(f'/users/{self.uid1}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("testuser1", html)
        self.assertIn("Abyssinian", html)
        self.assertIn("Edit", html)
        self.assertIn("Delete", html)

    def test_edit_user_profile_anon(self):
        """Prevent anonymous users from editing a user's profile."""
        with self.client as c:
            resp = c.get(f'/users/{self.uid1}/edit')

            self.assertEqual(resp.status_code, 302)
            
            resp_redirect = c.get(f'/users/{self.uid1}/edit', follow_redirects=True)
            html = resp_redirect.get_data(as_text=True)

            self.assertEqual(resp_redirect.status_code, 200)
            self.assertIn("Access unauthorized.", html)
    
    def test_edit_user_profile_other(self):
        """Prevent authenticated users from editing another user's profile."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid2

        resp = c.get(f'/users/{self.uid1}/edit')

        self.assertEqual(resp.status_code, 302)
        
        resp_redirect = c.get(f'/users/{self.uid1}/edit', follow_redirects=True)
        html = resp_redirect.get_data(as_text=True)

        self.assertEqual(resp_redirect.status_code, 200)
        self.assertIn("Access unauthorized.", html)

    def test_edit_user_profile_self(self):
        """Allow users to edit their own profile with current data prefilled into the edit form."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

        resp = c.get(f'/users/{self.uid1}/edit')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit Account Details", html)
        self.assertIn("testuser1", html)

    def test_update_user_profile_success(self):
        """User updated details successully."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

        d = {"email" : "test1@test.com",
            "username" : "testuser1updated",
            "password" : "HASHED_PASSWORD",
            "image_url" : ""}
        resp = c.post(f'/users/{self.uid1}/edit', data = d, follow_redirects = True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("testuser1updated", html)

    def test_update_user_profile_fail(self):
        """User updated details failure."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

        d = {"email" : "test1@test.com",
            "username" : "testuser1updated",
            "password" : "INVALID_PASSWORD",
            "image_url" : ""}
        resp = c.post(f'/users/{self.uid1}/edit', data = d, follow_redirects = True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Password incorrect! Your details have not been changed.", html)
    
    def test_delete_user_profile_anon(self):
        """Prevent anonymous users from deleting a profile."""
        with self.client as c:
            resp = c.post(f'users/delete', follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertIn('Access unauthorized.', html)

    def test_delete_user_profile_self(self):
        """User delete own profile successfully."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

        c.post(f'users/delete', follow_redirects = True)

        self.assertIsNone(User.query.get(self.uid1))