from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

ENV = 'prod'
developer = 'Arjun'
if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = 'awwfaw'
    if developer == 'Arjun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgre-arj4703@localhost/Zorg'
    elif developer == 'Tarun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tarun@postgresql@localhost/Zorg'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ijzfnghlvlklnn:d57fdfbf6ec19ca5595ffd1f69cc1de8a0abf76a8b6811c3cb75801e194c4863@ec2-34-236-166-210.compute-1.amazonaws.com:5432/d167aqa4jt3mhk'
    app.config['SECRET_KEY'] = 'segfsefsfsegaeahg32'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from zorgapp import routes
