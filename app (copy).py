from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from database import get_session  # Import the get_session function
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the base class for SQLAlchemy
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Define the FormData model for storing form submissions
class FormData(Base):
    __tablename__ = 'form_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text)
    address = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


# Route for the index page
@app.route('/')
def index():
    return redirect('/login')


# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password,
                                                 method='pbkdf2:sha256')

        db_session = get_session()

        # Check if user already exists
        user = db_session.query(User).filter_by(email=email).first()
        if user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Insert new user into the database
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db_session.add(new_user)
        db_session.commit()
        db_session.close()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db_session = get_session()

        # Check user credentials
        user = db_session.query(User).filter_by(email=email).first()
        db_session.close()

        if user and check_password_hash(user.password_hash, password):
            flask_session['user_id'] = user.id  # Using Flask session
            flask_session['user_name'] = user.name  # Using Flask session
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


# Route for home page
@app.route('/home')
def home():
    if 'user_id' not in flask_session:  # Using Flask session
        flash('Please log in to access the home page.', 'info')
        return redirect(url_for('login'))
    return render_template('public_admin_form.html', name=flask_session['user_name'])


# Route to logout
@app.route('/logout')
def logout():
    flask_session.clear()  # Using Flask session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Route for public administration form
@app.route('/public-form', methods=['GET', 'POST'])
def public_form():
    if request.method == 'POST':
        # Collect data from the form
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        address = request.form['address']

        # Create a new FormData object
        new_form_entry = FormData(
            name=name,
            email=email,
            message=message,
            address=address
        )

        # Get a database session and save the data
        db_session = get_session()
        db_session.add(new_form_entry)  # Add the new entry to the session
        db_session.commit()  # Commit the transaction to the database
        db_session.close()  # Close the session

        flash('Form submitted successfully!', 'success')  # Show a success message
        return redirect(url_for('public_form'))  # Redirect to the form page again (or anywhere else)

    return render_template('public_admin_form.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
