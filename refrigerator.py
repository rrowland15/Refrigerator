from flask import Flask, request, render_template, url_for, redirect
import sqlite3
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.sql import text

sqlconnection = sqlite3.connect('recipes.db')

app = Flask(__name__)

# db_name =

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +


@app.route("/", methods=['GET', 'POST'])
def gfg():
    if request.method == 'POST':
        first_ingredient = request.form.get("Ingredient1")
        first_expiration = request.form.get("Ingredient1expiration")
        return "Your name is "+first_ingredient+first_expiration
    return render_template("refrigerator2.html")


if __name__ == "__main__":
    app.run()
