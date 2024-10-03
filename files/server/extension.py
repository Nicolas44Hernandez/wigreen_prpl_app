"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_smorest import Api

api = Api()
""" The main Flask API, used to register blueprints """
