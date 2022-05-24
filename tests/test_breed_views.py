"""Breed View tests."""

import os
from unittest import TestCase

from models import db, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///cat_finder_test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False


class BreedViewTestCase(TestCase):
    """Test views for breeds."""

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

        db.session.commit()

        self.u1 = u1
        self.uid1 = u1.id

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

    def test_cat_is_not_favorited(self):
        """When loading a breed's information, it should not show that the breed is favorited."""
        with self.client as c:
            resp = c.get(f'/cats/abys')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="fa-solid fa-star" data-breed=', html)

    def test_cat_is_favorited(self):
        """If a user has a breed favorited, the breed's information page should show that it has been favorited."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.get(f'/cats/abys')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="fa-solid fa-star favorited" data-breed=', html)

    def test_invalid_cat(self):
        """If a breed is invalid, return an error page."""
        with self.client as c:
            resp = c.get('/cats/invalidbreed')
            self.assertEqual(resp.status_code, 302)
            
            resp_redirect = c.get('/cats/invalidbreed', follow_redirects=True)
            html = resp_redirect.get_data(as_text=True)

            self.assertEqual(resp_redirect.status_code, 200)
            self.assertIn("Sorry, but we don't currently have information on that cat breed.", html)

    def test_random_cat_generator(self):
        """The random cat generator redirects to a breed's information page."""
        with self.client as c:
            resp = c.get('/random')
            self.assertEqual(resp.status_code, 302)
            
            resp_redirect = c.get('/random', follow_redirects=True)
            html = resp_redirect.get_data(as_text=True)

            self.assertEqual(resp_redirect.status_code, 200)
            self.assertIn("Temperament:", html)
