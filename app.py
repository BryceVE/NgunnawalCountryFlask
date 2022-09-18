from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config.from_object(Config)  # loads the configuration for the database
db = SQLAlchemy(app)  # creates the db object using the configuration
login = LoginManager(app)
login.login_view = 'login'

UPLOAD_FOLDER = './static/images/userPhotos/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# these imports must be after (db = SQLAlchemy(app))
from models import Contact, todo, User, Photos
from forms import ContactForm, RegistrationForm, LoginForm, ResetPasswordForm, PhotoUploadForm


# Index / Home page
@app.route('/')
def homepage():
    return render_template("index.html", title="Home Page", user=current_user)


if __name__ == '__main__':
    app.run()


@app.route('/photo')
def photo_album():
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


# Contact Messages (administrator only)
@app.route('/contact_messages')
@login_required
def contact_messages():
    if current_user.is_admin():  # checks if the user is an admin
        all_messages = db.session.query(Contact).all()  # gets all messages from contact table
        return render_template("contact_messages.html", title="Contact Messages", user=current_user,
                               messages=all_messages)
    else:
        return redirect("/")  # if user is not an admin user gets redirected to home page


# user photos page
@app.route('/userPhotos', methods=['GET', 'POST'])
@login_required
def photos():
    form = PhotoUploadForm()
    user_images = Photos.query.filter_by(userid=current_user.id).all()  # gets all images from database that current user has submitted
    if form.validate_on_submit():  # if the form is properly filled out
        new_image = form.image.data  # gets file name
        filename = secure_filename(new_image.filename)  # stores filename as a secure filename

        if new_image and allowed_file(filename):  # checks if the file is an allowed filetype
            file_ext = filename.split(".")[1]  # Get the file extension of the file
            import uuid
            random_filename = str(uuid.uuid4())  # creates a random file name using the uuid library
            filename = random_filename + "." + file_ext  # overrides the file name with the randomly generated one
            new_image.save(os.path.join(UPLOAD_FOLDER, filename))  # uploads the file to the userPhotos folder
            photo = Photos(title=form.title.data, filename=filename,
                           userid=current_user.id)  # creates a new photo model
            db.session.add(photo)  # adds photo information into the database
            db.session.commit()  # commits new data to database
            flash("Image Uploaded")  # message to display to user
            return redirect(url_for("photos"))
        else:  # if filetype not allowed
            flash("The File Upload failed.")  # display error message to user
    return render_template("userPhotos.html", user=current_user, form=form, images=user_images)


# view single image
@app.route('/userPhotos/<photo_id>')
@login_required
def photo_display(photo_id):
    image = Photos.query.filter_by(photoid=photo_id).all()
    all_users = User.query.all()
    return render_template("photoDisplay.html", user=current_user, photo=image, title="View Image", users=all_users)


# photo gallery to display all images
@app.route('/gallery')
def photo_gallery():
    all_images = Photos.query.all()
    all_users = User.query.all()
    return render_template("gallery.html", title="Photo Gallery", user=current_user, images=all_images, users=all_users)


# used for checking that an attached file is the correct filetype
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return redirect("/todo")  # sends the user back to the to do page
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
    return redirect("/todo", code=302)  # redirects user to the normal to do page


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
            flash("There was a error logging you in")
            return redirect(url_for('login'))
        login_user(user)
        flash("Successfully logged in as " + user.name)
        return redirect(url_for('homepage'))
    return render_template("login.html", title="Log In", form=form, user=current_user)


# User profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("userProfile.html", title="User Profile", user=current_user)


# reset password
@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()
    user = User.query.filter_by(email_address=current_user.email_address).first()
    if form.validate_on_submit() and user.check_password(form.current_password.data):
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Incorrect username or password")
        return redirect(url_for('homepage'))
    return render_template("passwordreset.html", title='Reset Password', form=form, user=current_user)


# logout
@app.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for('homepage'))


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=current_user), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", user=current_user), 500
