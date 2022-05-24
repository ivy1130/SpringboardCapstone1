from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="https://icon-library.com/images/anonymous-person-icon/anonymous-person-icon-18.jpg",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    favorites = db.relationship('Favorite', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False   
    
class Favorite(db.Model):
    """Favorited cats by user."""

    __tablename__ = 'favorites'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )
    
    breed_name = db.Column(
        db.Text,
        primary_key=True
    )

    def serialize(self):
        """Returns a dict representation of cupcake, which can be turned into JSON"""
        return {
            'user_id': self.user_id,
            'breed_name': self.breed_name
        }

    def __repr__(self):
        return f"<Favorite {self.user_id}, {self.breed_name}>"