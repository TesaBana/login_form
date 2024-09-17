from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

'''
Initialize the Flask app.
'''
app = Flask(__name__)

'''
Set secret key for secure sessions.
This is required for Flask-Login and form security (CSRF protection).
'''
app.config['SECRET_KEY'] = 'your_secret_key'

'''
Database configuration using SQLite.
You can replace 'sqlite:///users.db' with another database URI (e.g., PostgreSQL or MySQL).
'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

'''
Initialize the SQLAlchemy ORM to handle the database.
'''
db = SQLAlchemy(app)

'''
Initialize Flask-Login to manage user sessions and authentication.
'''
login_manager = LoginManager(app)

'''
Specify the login view for when unauthorized users try to access protected routes.
'''
login_manager.login_view = 'login'


'''
User model to store user details.
Inherits from UserMixin to integrate with Flask-Login's session management.
Fields:
- id: primary key (unique user ID).
- username: unique identifier for the user (string).
- password: password for the user (stored as plaintext here but should be hashed).
- role: role of the user (e.g., Student, Teacher, etc.).
'''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)


'''
Create the database tables.
This will create the 'users.db' file and the necessary tables if they don't already exist.
'''
with app.app_context():
    db.create_all()


'''
Flask-Login user loader function.
Loads the user by ID (stored in session) to manage authentication state.
'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


'''
Route to register a new user.
This handles both GET (to display the form) and POST (to process form submission).
- If the username already exists, it will show a flash message.
- Otherwise, it will register the user and redirect to the login page.
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        ''' 
        Check if the username is already taken.
        '''
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        '''
        Create a new user object and save it to the database.
        '''
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        '''
        Flash success message and redirect to the login page.
        '''
        flash('User registered successfully!')
        return redirect(url_for('login'))
    
    '''
    Render the registration page when a GET request is made.
    '''
    return render_template('register.html')


'''
Route to log in a user.
- If credentials are valid, the user is logged in, and a flash message with their role is displayed.
- Otherwise, an error message is flashed.
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        '''
        Query the user by username and password (in a real app, passwords should be hashed).
        '''
        user = User.query.filter_by(username=username, password=password).first()
        
        '''
        If user exists, log them in and redirect to the appropriate dashboard.
        '''
        if user:
            login_user(user)
            flash(f'Logged in as {user.role}')
            return redirect(url_for('dashboard'))
        else:
            '''
            If login fails, flash an error message.
            '''
            flash('Invalid credentials!')
    
    '''
    Render the login page when a GET request is made.
    '''
    return render_template('login.html')


'''
Route for the user's dashboard.
The content is based on the user's role (e.g., Student, Teacher, Parent, etc.).
This route is protected, meaning only logged-in users can access it.
'''
@app.route('/dashboard')
@login_required
def dashboard():
    '''
    Serve a different dashboard template based on the user's role.
    '''
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
        '''
        If the role is unknown, display an error message.
        '''
        return 'Unknown role'


'''
Route to log out the user.
This route is protected, meaning the user needs to be logged in to access it.
'''
@app.route('/logout')
@login_required
def logout():
    '''
    Log the user out and redirect them to the login page.
    '''
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))


'''
Run the Flask app in debug mode, which allows live reloading on code changes.
'''
if __name__ == '__main__':
    app.run(debug=True)
