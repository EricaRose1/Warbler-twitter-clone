from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///users_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    '''hompeage'''
    return redirect('/register')

#####

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''register a user: produce form & handle form submission'''
    if "username" in session:
        return redirect(f"/users/{session['username']}")
        
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        new_user = User.register(username, password, first_name, last_name, email)
        db.session.commit()
        session['username'] = new_user.username

        return redirect(f"/users/{new_user.username}")
    else:
        return render_template('/users/register.html', form=form)

###
@app.route('/login', methods=['GET', 'POST'])
def login_user():

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']
            return render_template("users/login.html", form=form)

    return render_template('users/login.html', form=form)

###
@app.route('/logout')
def logout():
    '''logout'''
    session.pop("username")
    return redirect('/login')

###
@app.route('/users/<username>')
def show_user(username):
    '''example page for logged-in-users.'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)


    return render_template('users/show.html', user=user)

###
@app.route('/users/<username>/delete', methods=['POST'])
def remove_user(username):
    '''remove user and redirect to login'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")




@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def feedback_form(username):
    ''' display form to add feedback'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = session['username']

        feedback = Feedback(title=title, content=content,username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.id}')
    else:
        return render_template('/feedback/add.html', form=form)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    '''show update-feedback form & process it.'''

    feedback = Feedback.query.get(id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj = feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    return render_template("/feedback/edit.html", form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    '''delete feedback'''
    feedback = Feedback.query.get_or_404(feedback_id)
    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
   
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f'/users/{feedback.username}')   

