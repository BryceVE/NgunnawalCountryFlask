from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, LoginManager, logout_user, login_required

app = Flask(__name__)
app.config.from_object(Config)  # loads the configuration for the database
db = SQLAlchemy(app)  # creates the db object using the configuration
login = LoginManager(app)
login.login_view = 'login'

# these imports must be after (db = SQLAlchemy(app))
from models import Contact, todo, User
from forms import ContactForm, RegistrationForm, LoginForm, ResetPasswordForm


# Index / Home page
@app.route('/')
def homepage():
    return render_template("index.html", title="Home Page", user=current_user)


if __name__ == '__main__':
    app.run()


@app.route('/photo')
def photoAlbum():
    return render_template("photo.html", title="Photo Album", user=current_user)


@app.route('/history')
def history():
    return render_template("history.html", title="History", user=current_user)


# Contact us page
@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():  # if all input boxes have valid entries
        new_contact = Contact(name=form.name.data, email=form.email.data,
                              message=form.message.data)  # new variable to store data from form
        db.session.add(new_contact)  # adds new entry into the to do table
        db.session.commit()  # commits added entry to database
        flash("Your message has been submitted")
        return redirect("/")  # redirects user to home page
    return render_template("contact.html", title="Contact Us", form=form, user=current_user)


# To do page
@app.route('/todo', methods=["POST", "GET"])
def view_todo():
    all_todo = db.session.query(todo).all()  # retrieves whole of to do table from database
    if request.method == "POST":  # if form is attempting to submit data
        new_todo = todo(text=request.form['text'])  # new variable to store data from form
        new_todo.done = False  # sets done to false by default
        db.session.add(new_todo)  # adds new entry into the to do table
        db.session.commit()  # commits added entry (row) to database
        db.session.refresh(new_todo)  # refreshes the database
        return redirect("/todo.html")  # sends the user back to the to do page
    return render_template("todo.html", todos=all_todo, user=current_user)  # sends the user back to the to do page


# to do page for editing to do entries
@app.route("/todoedit/<todo_id>", methods=["POST",
                                           "GET"])  # route accepts variable (link/todoedit/<varialbe>) this refers to entry in table with id of <todo_id>
def edit_note(todo_id):
    if request.method == "POST":  # if form is attempting to submit data
        db.session.query(todo).filter_by(id=todo_id).update({  # finds entry in db with matching id to todo_id
            "text": request.form['text'],
            "done": True if request.form['done'] == "on" else False
        })
        db.session.commit()  # commits any changes to db
    elif request.method == "GET":  # if the form is submitted with GET method (trying to access something in the db)
        db.session.query(todo).filter_by(
            id=todo_id).delete()  # finds entry in db with matching id to todo_id and removes it
        db.session.commit()  # commits any changes to db
    return redirect("/todo.html", code=302)  # redirects user to the normal to do page


# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(email_address=form.email_address.data, name=form.name.data,
                        user_level=1)  # defaults to regular user
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account successfully created")
        return redirect(url_for("login"))
    return render_template("registration.html", title="Register Account", form=form, user=current_user)


# login page
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('homepage'))
    return render_template("login.html", title="Log In", form=form, user=current_user)


# reset password
@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()
    user = User.query.filter_by(email_address=current_user.email_address).first()
    if form.validate_on_submit() and user.check_password(form.current_password.data):
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password has been reset")
        return redirect(url_for('homepage'))
    else:
        flash("There was a error resetting your password")
    return render_template("passwordreset.html", title='Reset Password', form=form, user=current_user)


# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))
