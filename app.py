from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

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
def secret(username):
    if 'username' not in session:
        flash('Please login first.','danger')
        return redirect('/login')
    user=User.query.filter_by(username=username).first()
    
    return render_template('user.html',user=user)

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
        new_feedback = Feedback(title=title, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback added.', 'success')
        return redirect(f'/users/{username}')
    return render_template('/feedback/add.html',form=form)