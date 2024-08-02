import re
import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY_SITE")
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv("RECAPTCHA_PRIVATE_KEY")

# Configure SQLite database
db_directory = os.path.join(os.getcwd(), 'db')
os.makedirs(db_directory, exist_ok=True)
db_file = os.path.join(db_directory, 'contacts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define a model for contact form submissions


class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    inserted_at = db.Column(db.DateTime, default=func.now(), nullable=False)

# Define a form class for the contact form


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
                       DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[
                            DataRequired(), Length(min=10)])

# Initialize the database


@app.before_request
def initialize():
    if not hasattr(app, 'initialized'):
        db.create_all()
        app.initialized = True

# Route for the index page with form handling


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    phone_regex = re.compile(
        r"^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$")

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        print(request.form)
        # Custom validation
        if not name or not email or not message:
            flash('All fields are required!')
            return redirect(url_for('index'))

        if len(name) < 2 or len(name) > 200:
            flash('Name must be between 2 and 200 characters.')
            return redirect(url_for('index'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address.')
            return redirect(url_for('index'))

        if not re.match(phone_regex, phone):
            flash('Invalid phone number.')
            return redirect(url_for('index'))

        if len(message) < 10:
            flash('Message must be at least 10 characters long.')
            return redirect(url_for('index'))

        # Save the submission to the database
        try:
            submission = ContactSubmission(
                name=name, email=email, phone=phone, message=message)
            db.session.add(submission)
            db.session.commit()
            flash('Thank you for submitting your message!')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error occurred: {e}')
            print(f'Error occurred: {e}')  # Print the error for debugging

            flash('Thank you for submitting your message!')
            return redirect(url_for('index'))

    return render_template('index.html', form=form)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
