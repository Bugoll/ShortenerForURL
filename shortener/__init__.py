from flask import Flask, g
import secrets, os, sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
DATABASE = r'Shortener\shortener.sqlite'

def db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

from shortener import routes
from shortener import forms