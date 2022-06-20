# Cat Finder
#### A site to help potential cat owners filter cats based on energy level, intelligence, social needs, and hypoallergenic levels. 
##### https://springboard-ivy-capstone-1.herokuapp.com/

API

* Site was built with the The Cat API: https://thecatapi.com/

Features

* Filtering: Filter cats based on energy level, intelligence, social needs, and if they are hypoallergenic or not. With this feature, users can find a cat that's a good fit for their lifestyle.
* Favoriting: Create an account and have access to the favoriting feature, so you can always come back and see the cats that you are interested in.
* User Profiles: Any user with an account can view another's profile, so you can share your profile for friends and family to learn more about your potential pet.
* Random Cat Generator: Don't have any preferences? You can generate a random cat and learn more about it.

User Flow

* Filter cats based on personal preferences.
* Browse photos, view attributes of each cat, and visit attached resources for additional information.
* Create an account to favorite cats.
* Access your own user profile to view your favorited cats and to edit your account information.
* Visit the random cat generator to view and learn more about a random cat.

Tech Stack

* Python Flask Backend with:
 * Secure Bcrypt password hashing by default
 * SQLAlchemy models
 * WTForms with validation
* Frontend with:
 * Bootstrap
 * Jinja templates
