from unittest import TestCase

from app import app
from models import db, User, Post, PostTag, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyViewsTestCase(TestCase):

    def setUp(self):
        """Add sample user."""

        ### Delete objects: This has to be done in EXACTLY this order ###
        PostTag.query.delete()
        Tag.query.delete()
        Post.query.delete()
        User.query.delete()
        
        ### Create test user ###
        user = User(first_name="Tom", last_name="Test")
        db.session.add(user)
        db.session.commit()

        ### Create test post ###
        post = Post(title="My Post", content="Lorem Ipsum Delorem", user=user)
        db.session.add(post)
        db.session.commit()

        ### Create test tag, to be added to test post from above ###
        posts = [post]
        tag = Tag(name="Tagline", posts=posts)

        db.session.add(tag)
        db.session.commit()

        ### Store user id, user image url, user object, post id, and tag id ###
        ### for testing purposes ###
        self.user_id = user.id
        self.image_url = user.image_url
        self.user = user

        self.post_id = post.id

        self.tag_id = tag.id
        

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

#########################################################
#User Tests
#########################################################

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Tom Test', html)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Tom Test</h1>', html)
            self.assertIn(self.image_url, html)

    def test_add_user(self):
        with app.test_client() as client:
            d = {"first_name": "Teresa", "last_name": "Test", "image_url": self.image_url}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Teresa Test", html)

    def test_edit_user(self):
        with app.test_client() as client:
            d = {"first_name": "Teresa", "last_name": "Test", "image_url": self.image_url}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Teresa Test", html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Tom Test", html)

#########################################################
#Post Tests
#########################################################

    def test_add_post(self):
        with app.test_client() as client:
            d = {"title": "My Next Post", "content":"Lorem ipsum delorem"}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Next Post", html)

    def test_edit_post(self):
        with app.test_client() as client:
            d = {"title": "My Edited Post", "content":"Lorem ipsum delorem"}
            resp = client.post(f"/posts/{self.post_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Edited Post", html)

    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.post(f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("My Post", html)
    
#########################################################
#Tag Tests
#########################################################

    def test_show_tags(self):
        with app.test_client() as client:
            resp = client.get("/tags")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Tagline", html)

    def test_create_new_tag(self):
        with app.test_client() as client:
            d = {"name": "Newtag", "posts": [self.post_id]}
            resp = client.post(f"/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Newtag", html)

    def test_show_individual_tag(self):
        with app.test_client() as client:
            resp = client.get(f"/tags/{self.tag_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Tagline', html)

    def test_edit_tag(self):
        with app.test_client() as client:
            d = {"name": "Newtag", "posts": [self.post_id]}
            resp = client.post(f"/tags/{self.tag_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Newtag", html)

    def test_delete_tag(self):
        with app.test_client() as client:
            resp = client.post(f"/tags/{self.tag_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Tagline", html)



    