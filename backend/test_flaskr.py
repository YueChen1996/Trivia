import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_all_question(self):
        response = self.client().get('/questions')
        data = json.loads(res.data)
        self.asserEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_fail_get_questions(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    def test_all_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)

    def test_fail_get_categories(self):
        res=self.client().post('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'METHOD NOT ALLOWED')


    def test_delete_questions(self):
        res = self.client().delete('/questions/15')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],15)

    def test_fail_delete(self):
        res=self.client().post('/questions/12')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resouce not found')

    def test_search(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'city'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_fail_search(self):
        res = self.client().get('/questions/search',
                                json={'searchTerm': 'city'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'METHOD NOT ALLOWED')

    def test_new_questions(self):
        res =self.client().post('/questions', json=self.new_questions)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_fail_new_questions(self):
        res = self.client().get('/questions', json={"new"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()