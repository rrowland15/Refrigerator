from flask import Flask, request, render_template
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

sqlconnection = sqlite3.connect('recipes.db')

app = Flask(__name__)

db_name =

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +



@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return ''

    else:
        #return "This is a get request"
        return render_template('refrigerator2.html')

if __name__ == "__main__":
    app.run()
