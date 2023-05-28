from flask import Flask, request, jsonify,session
from flask_session import Session
import bcrypt
from datetime import datetime
import bcrypt
import jwt
import datetime
from models import db
from models.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)


@app.route('/')
def hello():
    return jsonify('Hello, Flask!')


####################################################################
@app.route('/login', methods=['POST'])
def login():
    # Retrieve login credentials from the request
    username = request.json.get('username')
    password = request.json.get('password')

    # Validate login credentials
    if username and password:
        # Implement logic to check credentials against the database
        user = User.query.filter_by(username=username).first()

        if user:
            # Compare the provided password with the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                # If the passwords match, login is successful
                token = generate_auth_token(user.username)
                session['username'] = user.username
                return jsonify(token=token), 200

    # If login fails, return an appropriate error response
    return jsonify(error='Invalid username or password'), 401


def generate_auth_token(username):
    # Set the expiration time for the token
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours

    # Define the payload of the token
    payload = {
        'username': username,
        'exp': expiration
    }

    # Generate the token using the JWT library
    token = jwt.encode(payload, 'my_secret_key', algorithm='HS256')

    # Return the generated token
    return token

####################################################################
@app.route('/signup', methods=['POST'])
def signup():

    # Retrieve sign-up data from the request
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    full_name = request.json.get('full_name')
    phone_number = request.json.get('phone_number')


    # Validate sign-up data Checking if the required fields are present
    if not username or not password or not email or not full_name or not phone_number:
        return jsonify(error='Missing required fields'), 400   

    # Implement logic to check if the username or email already exists in the database
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(error='Username already exists'), 400

    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify(error='Email already exists'), 400
    
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        return jsonify(error='Phone number already exists'), 400
 
    # Hash the password securely before storing it in the database
    hashed_password = hash_password(password)

    # Create a new user record with the provided username, hashed password, and email
    new_user = User(username=username, password=hashed_password, email=email,  full_name=full_name, phone_number=phone_number)
    
    try:
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(message='User created successfully'), 201
    except Exception as e:
        return jsonify(error='Failed to create user'), 500


def hash_password(password):
    # Generate a salt for hashing
    salt = bcrypt.gensalt()

    # Hash the password using the generated salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Return the hashed password as a byte string
    return hashed_password.decode('utf-8')


# Create all tables and flush the users table
with app.app_context():
    db.create_all()
    db.session.commit()

# db.init_app(app)
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
    # app.run()

