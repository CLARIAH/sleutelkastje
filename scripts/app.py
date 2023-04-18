from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response
#import sqlite3 as sql
import os
#from werkzeug.utils import secure_filename
#from insert_json import upload_json

app = Flask(__name__)
@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/add/', methods=['GET','POST'])
def add_app():
    result = ''
    app = ''
    cred = ''
    url = ''
    response = make_response(render_template('upload.html'),200)
    if request.method == 'POST':
        app = request.form['app']
        cred = request.form['credentials']
        url = request.form['redirect']
        return make_response(render_template('succes.html',result=app),200)
    return response

@app.route('/find/<app>', methods=['GET'])
def geet_app(app):
    result = ''
    filename = ''
    response = make_response(render_template('get.html',result=result),200)
    #response.status = '200'
    if request.method == 'GET':
        # reponse code ?
        response = make_response(render_template('get.html',result=app),201)
    return response

if __name__ == "__main__":
    app.run()


