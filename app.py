import re
import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from dotenv import load_dotenv
from flask_mail import Mail, Message
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY_SITE")
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv("RECAPTCHA_PRIVATE_KEY")

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_TLS_PORT")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS")
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL")

mail = Mail(app)


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
                       DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[
                            DataRequired(), Length(min=10)])
    # recaptcha = RecaptchaField()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    phone_regex = re.compile(
        r"^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$")
    print(request.form)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
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
        # Add server-side validation or processing here
        # Compose email
        print(request.form)
        msg = Message(subject='Contact Form Submission',
                      sender=email,
                      recipients=['delacruzspablo@gmail.com'],
                      body=f"Name: {name}\nEmail: {email}\nMessage: {message}\n{request.form}")

        # Send email
        mail.send(msg)
        flash('Thank you for submitting your message!')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = request.form['phone']
        message = form.message.data
        # Add server-side processing or send email here
        flash('Thank you for submitting your message!')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)
