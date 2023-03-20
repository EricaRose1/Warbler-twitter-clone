"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()



# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False




class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # User.query.delete()
        # Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            response = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(response.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_add_no_session(self):
        with self.client as c:
            response = c.post('/messages/new', data={'text': 'hello'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))
    
    def test_message_show(self):

        m = Message(id = 1234, text='a test message', user_id=self.testuser_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            
            m = Message.query.get(1234)
            response = c.get(f'/messages/{m.id}')

            self.assertEqual(response.status_code, 200)
            self.assertIn(m.text, str(response.data))


    def test_message_delete(self):
        m = Message(id=1234, text='a test message', user_id=self.testuser_id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            response = c.post('/messages/1234/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            m = Message.query.get(1234)
            self.assertIsNone(m)

    def test_unauthorized_message_delete(self):

        user = User.signup(username='unauthorized_user', 
                        email='testtest@test.com', 
                        password='password', 
                        image_url=None)

        user.id = 76543

        #Message is owned by testuser
        m = Message(id=1234, text='a test message', user_id=self.testuser_id )

        db.session.add_all([user, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = 76543
            
            response = c.post('/messages/1234/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):
        m = Message(id = 1234, text='a test message', user_id=self.testuser_id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            response = c.post('/messages/1234/delete', follow_redirects= True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', str(response.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)







