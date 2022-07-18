# Make a virtual environment and install flask:

# really good explanation of venv: https://www.youtube.com/watch?v=KxvKCSwlUv8

# 'which python3' get the path to your python3 executable
# 'cd flask_hello_world' navigate to the folder you want to rely on the venv
# ' /usr/bin/python3 -m venv venvName' create the venv with any name you want
# 'source venvName/bin/activate' activate the venv
# 'deactiave' will deactivate the venv

# you path now points to python3 and pip3 so you can run python or pip and they will refer to version 3
# `echo $PATH` you can see the path for dependecies 
# `pip install flask peewee` install flask and peewee into your virtual env

import os, base64
from flask import Flask, render_template, request, redirect, url_for, session
# import schema/ db object model for adding info to the sqlite db
from db.model import SavedTotal


app = Flask("myAppName")

# HOST ON HEROKU
# the secret key saved in the code base is now accessible to anyone with out code, use env variable instead
# app.secret_key = b'v]\x9a\xad\xc3\r\xd9g\x13n\xb6V\x99\x85\xfdK\xf2v\x92\x80\xd9\xb3M\x01' old key here not used anymore

# 1)  add secret key environ variable to local machine run:
# export SECRET_KEY=<my_key_value>

# 2) add secret key environ variable to heroku:
# after installing heroku cli and running git init for the app run 'heroku create' (within the cacluator git repository directory)
# this will create a heroku app and add a git remote to the repository:

# (venv) markstewart@MacBook-Pro calculator % heroku create
# Creating app... done, ⬢ dry-castle-43290
# https://dry-castle-43290.herokuapp.com/ | https://git.heroku.com/dry-castle-43290.git

# set the environ variable in heroku:
# generate a key in python console first:
    # python
    # import os
    # os.urandom(24)
# heroku config:set SECRET_KEY=<my_secret_key> --app dry-castle-43290

# 3) install gunicorn (wsgi server) and pyscopg2 (connect to postgress db)
    # pip install gunicorn psycopg2
    # https://stackoverflow.com/questions/49811955/unable-to-install-psycopg2-pip-install-psycopg2

# 4) Ammend the list of requiredments to include pyscopg2 and gunicorn
    # pip freeze > requirements.txt

# 5) heroku needs to know the command to run the application:
    # create Procfile 
    # 'web: gunicorn main:app'
    # tells heroku to start web server, run gunicorn and point it to the app in main.py
# 6) local has been using sqlite, heroku uses a postgress db, create a postgress db on heroku:
    # `heroku addons:create heroku-postgresql:hobby-dev --app dry-castle-43290`     (https://stackoverflow.com/questions/31669067/heroku-postgresql-user-and-database-creation)
    # output: 
        # Creating heroku-postgresql:hobby-dev on ⬢ dry-castle-43290... free
        # Database has been created and is available
        # ! This database is empty. If upgrading, you can transfer
        # ! data from another database with pg:copy
        # Created postgresql-sinuous-98800 as DATABASE_URL
        # Use heroku addons:docs heroku-postgresql to view documentation
# 7) inspect heroku db and secret key with `heroku config --app dry-castle-43290`:
    # output: 
        # === dry-castle-43290 Config Vars
        # DATABASE_URL: postgres://kdubbjpwffupre:ba00a14da85499d3cff6540d0e67ed2e8aec3df09fd05f1151e46159bdd95874@ec2-52-72-99-110.compute-1.amazonaws.com:5432/d36bq3tiqu0mgp
        # SECRET_KEY:   <shows my key here>

# 8) push all this code to heroku:
    # git remote add heroku https://git.heroku.com/dry-castle-43290.git
    # git push heroku main

app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/add', methods=['GET', 'POST'])
def add():
    # if first time user visits page, initialize session total you can use the session because a random token was added to the secret_key value on app
    if 'total' not in session:
        session['total'] = 0

    # flask lets us see what kind of request was sent (Post, Put, Get, etc.)
    if request.method == 'POST':
        # access the form submitted: "<input type="number" id="number" name="number">" in add.jinja2
        number = int(request.form['number'] or 0) # cast to int, we don't know what the user entered (or to prevent cast error)
        session['total'] += number

    return render_template('add.jinja2', session=session) # inject entire session into our template as the session variable - add.jinja2 should retrieve this session value
    # if you don't set the templat session to our session variable, the total will not be passed through and will not increment

@app.route('/save', methods=['POST'])
def save():
    total = session.get('total', 0)
    # create a string of chars for the save total
    code = base64.b32encode(os.urandom(8)).decode().strip("=")

    # create a new entry using the db schema/model
    saved_total = SavedTotal(value=total, code=code)
    saved_total.save()
    # if you get a 500 internal error, make sure you have setup the db with python dbSetup.py
    # use sqliteStudio to see the table values in the db

    return render_template('save.jinja2', code=code)

@app.route('/retrieve')
def retrieve():
    # because the retrieve form uses the GET method, we have to use Flasks
    # request.args instead of the request.form
    # default value of None if they haven't submited the form yet
    retrieveCode = request.args.get('code', None)

    # If the suer is visiting the retrieve page (did not submit form yet):
        #Then just reder the retrieve.jinja2 template
    # But if they did submit the form:
        # Then attempt to retriee teh SavedTotal that has the provided code
        # Then save the total from that SavedTotal into the session['total']
        # Then redirect the user back to the main 'add' page
    if retrieveCode is None:
        return render_template('retrieve.jinja2')
    else:
        # try catch in case code doesn't exist in the db
        try:
            saved_total = SavedTotal.get(SavedTotal.code == retrieveCode)
        except SavedTotal.DoesNotExist:
            return render_template('retrieve.jinja2', error="Code not found")

        session['total'] = saved_total.value

        return redirect(url_for('add'))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# try to hit port 5000 on localhost, make sure you add the `/add` route - it's the only one defined

# Try it out:
# create a session key with some random data from python
# in the terminal (with venv activated) run:
# python
# import os
# os.urandom(24)
# assign the random key to the app.secret_key, now you can utilize the 'session' map for storing cookies



# Try it out:
# go to add route and increment numbers by adding, you will see the session persists across browser refreshes
# it will persist until the session is cleared
# save a and copy the saved id that is gernated
# increment the total some more in the session
# go to the retrieve route and enter the code: you will see that it sets the session total back to the value saved for that token
# try entering a bad code and you will see the error message