from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize the Flask app
app = Flask(__name__)

# Set secret key for secure sessions
app.config['SECRET_KEY'] = 'your_secret_key'

# Database configuration using SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize SQLAlchemy (ORM) for database handling
db = SQLAlchemy(app)

# Initialize Flask-Login to manage user sessions
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model to store user details
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # User roles like Student, Teacher, etc.


# Create the database if it doesn't exist
with app.app_context():
    db.create_all()


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))

        # Create new user and save to database
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find user by username and password
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            flash(f'Logged in as {user.role}')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!')

    return render_template('login.html')


# Route for user dashboards based on role
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Student':
        return render_template('student_dashboard.html')
    elif current_user.role == 'Teacher':
        return render_template('teacher_dashboard.html')
    elif current_user.role == 'Parent':
        return render_template('parent_dashboard.html')
    elif current_user.role == 'Accountant':
        return render_template('accountant_dashboard.html')
    elif current_user.role == 'Bursar':
        return render_template('bursar_dashboard.html')
    elif current_user.role == 'Director':
        return render_template('director_dashboard.html')
    else:
        return 'Unknown role'


# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
