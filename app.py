from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def redirect_register():
    return redirect("/register")

@app.route("/register", methods=['GET','POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user=User.register(username,password,email,first_name,last_name)

        db.session.add(new_user)
        
        db.session.commit()
        session['username']=username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'/users/{username}')
    
    return render_template('register-form.html',form=form)

@app.route('/users/<username>')
def show_user(username):
    if "username" not in session:
        flash('Please login first.','danger')
        return redirect('/login')
    if username != session['username']:
        flash('You can only view your own profile.','danger')
        return redirect(f'/users/{session["username"]}')
    user=User.query.filter_by(username=username).first()
    
    return render_template('user.html',user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if "username" not in session:
        flash('Please login first.','danger')
        return redirect('/login')
    if username != session['username']:
        flash('You can only delete your own profile.','danger')
        return redirect(f'/users/{session["username"]}')
    user=User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash('User successfully deleted','danger')
    return redirect('/')

@app.route("/login", methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        user = User.authenticate(username,password)
        if user:
            session['username']=username
            flash(f"Welcome Back, {user.username}!", "success")
            return redirect(f'/users/{username}')
        else:
            form.username.errors=['invalid username/password.']
    
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['Get','POST'])
def add_feedback(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, username=username,content=content)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback added.', 'success')
        return redirect(f'/users/{username}')
    return render_template('/feedback/add.html',form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['Get','POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    if feedback.username != session["username"]:
        flash('This is not your feedback.','danger')
        return redirect(f'/users/{session["username"]}')

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
     
        db.session.commit()
        flash('Feedback updated.', 'success')
        return redirect(f'/users/{feedback.username}')
    return render_template('/feedback/edit.html',form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    if feedback.username != session["username"]:
        flash('This is not your feedback.','danger')
        return redirect(f'/users/{session["username"]}')

   
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted.', 'success')
    return redirect(f'/users/{feedback.username}')
    