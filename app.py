from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import func

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

# Information for uploaded images
UPLOAD_FOLDER = './static/images/userPhotos/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# these imports must be after (db = SQLAlchemy(app))
from models import Contact, todo, User, Photos
from forms import ContactForm, RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordFormAdmin, PhotoUploadForm, TodoForm


# Index / Home page
@app.route('/')
def homepage():
    return render_template("index.html", title="Home Page", user=current_user)


if __name__ == '__main__':
    app.run()


# History Page
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
        flash("Your message has been submitted!")
        return redirect(url_for("contact"))  # reloads page
    return render_template("contact.html", title="Contact Us", form=form, user=current_user)


# Contact Messages (administrator only)
@app.route('/contact_messages')
@login_required
def contact_messages():
    if current_user.is_admin():  # checks if the user is an admin
        all_messages = db.session.query(Contact).all()  # gets all messages from contact table
        all_messages_count = Contact.query.count()  # gets count of all messages in database
        return render_template("contact_messages.html", title="Contact Messages", user=current_user,
                               messages=all_messages, messages_count=all_messages_count)
    else:
        return redirect(url_for('homepage'))  # if user is not an admin user gets redirected to home page


# admin message delete
@app.route("/admin/messagedeleteadmin/<message_id>", methods=['GET', 'POST'])
@login_required
def message_delete_admin(message_id):
    if not current_user.is_admin:  # if user is not an admin
        flash("You need to be an admin to do this!")
        return redirect(url_for('homepage'))
    if request.method == "GET":  # if the form is submitted with GET method (trying to access something in the db)
        db.session.query(Contact).filter_by(id=message_id).delete()  # finds entry in db with matching id to photo_id and removes it
        db.session.commit()  # commits any changes to db
        flash("Message successfully deleted!")
    return redirect(url_for('contact_messages'))


# List all users (administrator only)
@app.route('/admin/list_all_users')
@login_required
def list_all_users():
    if current_user.is_admin():  # checks if the user is an admin
        all_users = User.query.all()  # gets all users in the database
        all_users_count = User.query.count()  # gets count of all users in database
        return render_template("listAllUsers.html", title="All Users", user=current_user, users=all_users, users_count=all_users_count)
    else:  # if user is not an admin
        flash("You must be an administrator to access this page")
        return redirect(url_for("homepage"))


# reset user passwords (administrators only)
@app.route('/reset_password_admin/<userid>', methods=['GET', 'POST'])
@login_required
def reset_user_password(userid):
    form = ResetPasswordFormAdmin()
    user_to_reset = User.query.filter_by(id=userid).first()  # gets user chosen to have password reset
    if not current_user.is_admin():  # if user is not admin
        flash("You must be an administrator to access this page")  # error message
        return redirect("/reset_password")
    if form.validate_on_submit():  # if user is admin
        user_to_reset.set_password(form.new_password.data)  # sets new password
        db.session.commit()
        flash('Password has been reset for user {}'.format(user_to_reset.name))  # message to admin
        return redirect(url_for('homepage'))
    return render_template("passwordResetAdmin.html", title='Reset User Password', form=form, user=current_user, user_to_reset=user_to_reset)


# user photos page
@app.route('/userPhotos', methods=['GET', 'POST'])
@login_required
def photos():
    form = PhotoUploadForm()
    user_images = Photos.query.filter_by(userid=current_user.id).all()  # gets all images from database that current user has submitted
    user_images_count = Photos.query.filter_by(userid=current_user.id).count()  # gets the could of all images he user has uploaded
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
                           userid=current_user.id, enabled=1)  # creates a new photo model
            db.session.add(photo)  # adds photo information into the database
            db.session.commit()  # commits new data to database
            flash("Image uploaded to the photo gallery!")  # message to display to user
            return redirect(url_for("photos"))
        else:  # if filetype not allowed
            flash("The file upload failed")  # display error message to user
    return render_template("userPhotos.html", user=current_user, form=form, images=user_images, images_count=user_images_count)


# delete an uploaded photo
@app.route("/photodelete/<photo_id>", methods=['GET', 'POST'])
@login_required
def photo_delete(photo_id):
    if request.method == "GET":  # if the form is submitted with GET method (trying to access something in the db)
        db.session.query(Photos).filter_by(photoid=photo_id).delete()  # finds entry in db with matching id to photo_id and removes it
        db.session.commit()  # commits any changes to db
        flash("Image successfully deleted!")
    return redirect("/userPhotos")


# admin photo delete
@app.route("/admin/photodeleteadmin/<photo_id>", methods=['GET', 'POST'])
@login_required
def photo_delete_admin(photo_id):
    if not current_user.is_admin:  # if user is not an admin
        flash("You need to be an admin to do this!")
        return redirect(url_for('homepage'))
    if request.method == "GET":  # if the form is submitted with GET method (trying to access something in the db)
        db.session.query(Photos).filter_by(photoid=photo_id).delete()  # finds entry in db with matching id to photo_id and removes it
        db.session.commit()  # commits any changes to db
        flash("Image successfully deleted!")
    return redirect(url_for('list_all_photos'))


# view single image
@app.route('/userPhotos/<photo_id>')
@login_required
def photo_display(photo_id):
    image = Photos.query.filter_by(photoid=photo_id).all()  # gets image by the photo id in the URL
    max_image = db.session.query(func.max(Photos.photoid)).scalar()  # gets max value of photo id as a readable int (scalar)
    all_users = User.query.all()  # gets all users
    return render_template("photoDisplay.html", user=current_user, photo=image, max_photo=max_image, title="View Image", users=all_users)


# photo gallery to display all images
@app.route('/gallery')
def photo_gallery():
    all_images = Photos.query.all()  # gets all photos
    all_users = User.query.all()  # gets all users
    return render_template("gallery.html", title="Photo Gallery", user=current_user, images=all_images, users=all_users)


# List all photos (administrator only)
@app.route('/admin/list_all_photos')
@login_required
def list_all_photos():
    if current_user.is_admin():  # checks if the user is an admin
        all_photos = Photos.query.all()  # gets all photos in the database
        all_photos_count = Photos.query.count()  # gets count of all photos in database
        all_users = User.query.all()  # gets all users in the database
        return render_template("listAllPhotos.html", title="All Photos", user=current_user, photos=all_photos, photos_count=all_photos_count, users=all_users)
    else:  # if user is not an admin
        flash("You must be an administrator to access this page")
        return redirect(url_for("homepage"))


# enable / disable image
@app.route('/admin/photo_enable_disable/<photo_id>')
@login_required
def photo_enable_disable(photo_id):
    if not current_user.is_admin():  # checks if user is not an admin
        flash("You must be an administrator to access this page")
        return redirect(url_for('homepage'))
    photo = Photos.query.filter_by(photoid=photo_id).first()  # finds user selected
    photo.enabled = not photo.enabled  # switches boolean value in table
    db.session.commit()
    return redirect(url_for("list_all_photos"))


# used for checking that an attached file is the correct filetype
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# To do page
@app.route('/todo', methods=["POST", "GET"])
def todo_page():
    if current_user.is_anonymous:  # if the user isn't logged in
        all_todo = db.session.query(todo).filter_by(user_id=0).all()  # gets nothing
    else:
        all_todo = db.session.query(todo).filter_by(user_id=current_user.id).all()  # gets all todos of user logged in
    form = TodoForm()
    if form.validate_on_submit():  # if form is attempting to submit data
        if current_user.is_anonymous:  # if user is not logged in
            flash("You must be logged in to use this feature")  # error message
            return redirect(url_for("login"))  # redirect to login page
        else:
            new_todo = todo(text=form.text.data, user_id=current_user.id)  # new variable to store data from form
            db.session.add(new_todo)  # adds new entry into the to do table
            db.session.commit()  # commits added entry (row) to database
            db.session.refresh(new_todo)  # refreshes the database
            return redirect("/todo")  # sends the user back to the to do page
    return render_template("todo.html", todos=all_todo, form=form, user=current_user)  # sends the user back to the to do page


# to do page for editing to do entries
@app.route("/todoedit/<todo_id>", methods=["POST",
                                           "GET"])  # route accepts variable (link/todoedit/<varialbe>) this refers to entry in table with id of <todo_id>
def edit_todo(todo_id):
    if request.method == "POST":  # if form is attempting to submit data
        db.session.query(todo).filter_by(id=todo_id).update({  # finds entry in db with matching id to todo_id and updates it
            "text": request.form['text'],
            "done": True if request.form['done'] == "1" else False
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
    if form.validate_on_submit():  # if form is valid
        new_user = User(email_address=form.email_address.data, name=form.name.data,
                        user_level=1, active=1)  # defaults to regular user
        new_user.set_password(form.password.data)  # sets password
        db.session.add(new_user)  # saves to database
        db.session.commit()  # commits to database
        flash("Account successfully created")  # display a flash message
        return redirect(url_for("login"))  # redirects user to login page
    return render_template("registration.html", title="Register Account", form=form, user=current_user)


# login page
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # if form is valid
        user = User.query.filter_by(email_address=form.email_address.data).first()  # gets the user with the same email address in the database
        if user is None:  # checks if the users email exists
            flash("This user does not exist!")  # displays an error message
            return redirect(url_for('login'))  # redirects user to login page to try again
        if not user.check_password(form.password.data):  # verify the password
            flash("Your email or password is wrong!")  # displays an error message
            return redirect(url_for('login'))  # redirects user to login page to try again
        if not user.active:  # if user account is not active
            flash("This account is no longer active! Contact an admin if you need help")  # displays an error message
            return redirect(url_for('login'))  # redirects user to login page to try again
        login_user(user)  # else if user information is valid login the
        flash("Successfully logged in as " + user.name + "!")  # displays message to user
        return redirect(url_for('homepage'))  # redirects user to home page
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
    form = ResetPasswordForm()  # gets form submitted
    user = User.query.filter_by(email_address=current_user.email_address).first()  # gets user with the same email address
    if form.validate_on_submit() and user.check_password(form.current_password.data):  # checks form is valid and that the current password is correct
        user.set_password(form.new_password.data)  # sets new password into database
        db.session.commit()  # commits changes to database
        flash("Successfully reset password")  # display message to user
        return redirect(url_for('homepage'))  # redirects user to home page
    return render_template("passwordreset.html", title='Reset Password', form=form, user=current_user)


# enable / disable user account
@app.route('/admin/user_enable_disable/<userid>')
@login_required
def user_enable_disable(userid):
    if not current_user.is_admin():  # checks if user is not an admin
        flash("You must be an administrator to access this page")
        return redirect(url_for('homepage'))
    user = User.query.filter_by(id=userid).first()  # finds user selected
    user.active = not user.active  # switches boolean value in table
    db.session.commit()
    return redirect(url_for("list_all_users"))


# logout
@app.route('/logout')
def logout():
    logout_user()  # logs user out
    flash("Successfully logged out")  # displays message
    return redirect(url_for('homepage'))


# Error handlers
# 404 Page Not Found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=current_user), 404


# 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", user=current_user), 500
