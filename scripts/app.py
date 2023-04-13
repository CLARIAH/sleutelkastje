from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response
#import sqlite3 as sql
import os
#from werkzeug.utils import secure_filename
#from insert_json import upload_json

app = Flask(__name__)
@app.route('/', methods=['GET', 'PUT'])
def upload_file():
    result = ''
    filename = ''
    response = make_response(render_template('get.html',result=result),200)
    #response.status = '200'
    if request.method == 'PUT':
        # reponse code ?
        response = make_response(render_template('put.html',result=result),201)
    elif request.method == 'GET':
        # reponse code ?
        response = make_response(render_template('get.html',result=result),201)
    return response

if __name__ == "__main__":
    app.run()


