import os
import psycopg2

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:defence@localhost/postgres'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
    db.create_all()

    # db.drop_all()


if __name__ == "__main__":
    with app.app_context():
        main()
