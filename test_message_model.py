'''Message model tests.'''

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

'''set enviromental variable to use differnt database for test'''
os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    '''Test views for messages.'''

    def setUp(self):
        '''Create test client, add sample data.'''
        db.drop_all()
        db.create_all()

        self.uid = 95564
        u = User.signup('testing', 'testing@test.com', 'password', None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        '''Does basic model work?'''
        m = Message(text = 'a warble', user_id = self.uid)
        db.session.add(m)
        db.session.commit()

        #user should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'a warble')

    def test_likes(self):
        msg1 = Message(text='a warble', user_id=self.uid)
        msg2 = Message(text='a very interesting warble', user_id=self.uid)

        user = User.signup('yetanothertest', 't@email.com', 'password', None)
        userid = 888
        user.id = userid
        db.session.add_all([msg1, msg2, user])
        db.session.commit()

        user.likes.append(msg1)
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == userid).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, msg1.id)

