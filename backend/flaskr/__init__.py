import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type = int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    category = {subcategory.id: subcategory.type for subcategory in categories}

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': category
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_question = paginate_questions(request, questions)  
    categories = Category.query.order_by(Category.id).all()
    category = {subcategory.id: subcategory.type for subcategory in categories}

    if len(questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_question,
      'total_questions': len(questions),
      'current_category': None,
      'categories': category
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question == None:
        abort(404)

      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_question = paginate_questions(request, questions)


      return jsonify({
        'id': question_id,
        'message': "Question deleted successfully",
        'success': True,
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def new_question():
    body = request.get_json()
    
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    try:
      question = Question(answer=new_answer, category=new_category, difficulty=new_difficulty, question=new_question)
      question.insert()

      return jsonify({
        'success': True,
        'questions': question.format()
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_term = body.get('searchTerm', '')
    
    if search_term:
      results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      questions = [question.format() for question in results]

    return jsonify({
      'success': True,
      'questions': questions
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quizzes():
    body = request.get_json()
    category = body.get('quiz_category')
    previous_questions = body.get('previous_questions')
    
    if category['type'] == 'click':
      questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_(previous_questions)).all()
    
    
    if len(questions) > 0:
      new_question = questions[random.randrange(0, len(questions))].format()
    else:
      return jsonify(None)

    return jsonify({
      'success': True,
      'question': new_question
      })

 

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "We couldn't process your request."
      }), 422

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request."
      }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed."
      }), 405
  
  @app.errorhandler(500)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Something went wrong."
      }), 500
  
  return app


    
