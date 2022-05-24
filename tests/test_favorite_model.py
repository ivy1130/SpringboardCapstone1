"""Favorite model tests."""

import os
from unittest import TestCase
from models import db, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///cat_finder_test"

from app import app

db.create_all()

class FavoriteModelTestCase(TestCase):
    """Test model for Favorite."""

    def setUp(self):
        """Create test client, add sample data."""

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

    def test_favorite_model(self):
        """The Favorite model works."""

        u = self.u1
        f = self.f1

        self.assertEqual(len(u.favorites), 1)
        self.assertEqual(f.user_id, self.uid1)
        self.assertEqual(f.breed_name, 'Abyssinian')
    
    def test_favorite_model_repr(self):
        """The Favorite model repr is correct."""

        f = self.f1

        self.assertEqual(str(f), f"<Favorite {self.uid1}, Abyssinian>")
