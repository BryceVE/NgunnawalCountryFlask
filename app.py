from flask import Flask, render_template, request, redirect
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)  # loads the configuration for the database
db = SQLAlchemy(app)  # creates the db object using the configuration

from models import Contact, todo
from forms import ContactForm


@app.route('/')
def homepage():  # put application's code here
    return render_template("index.html", title="Ngunnawal Country")


if __name__ == '__main__':
    app.run()


@app.route("/contact.html", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(new_contact)
        db.session.commit()
        return render_template("index.html", title="Ngunnawal Country")

    return render_template("contact.html", title="Contact Us", form=form)


@app.route('/todo.html', methods=["POST", "GET"])
def view_todo():
    all_todo = db.session.query(todo).all()  # retrieves whole of to do table from database
    if request.method == "POST":  # if form is attempting to submit data
        new_todo = todo(text=request.form['text'])  # new variable to store data from form
        new_todo.done = False  # sets done to false by default
        db.session.add(new_todo)  # adds new entry into the to do table
        db.session.commit()  # commits added row to database
        db.session.refresh(new_todo)  # refreshes the database
        return render_template("todo.html", todos=all_todo)  # sends the user back to the to do page

    return render_template("todo.html", todos=all_todo)  # sends the user back to the to do page


@app.route("/todoedit/<todo_id>", methods=["POST", "GET"])  # route accepts variable (link/todoedit/<varialbe>) this refers to entry in table with id of <todo_id>
def edit_note(todo_id):
    if request.method == "POST":  # if form is attempting to submit data
        db.session.query(todo).filter_by(id=todo_id).update({  # finds entry in db with matching id to todo_id
            "text": request.form['text'],
            "done": True if request.form['done'] == "on" else False
        })
        db.session.commit()  # commits any changes to db
    elif request.method == "GET":  # if the form is submitted with GET method (trying to access something in the db)
        db.session.query(todo).filter_by(id=todo_id).delete()  # finds entry in db with matching id to todo_id and removes it
        db.session.commit()  # commits any changes to db
    return redirect("/todo.html", code=302)  # redirects user to the normal to do page
