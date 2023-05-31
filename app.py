from flask import Flask, request, jsonify, session
from flask_session import Session
import bcrypt
from datetime import datetime
import bcrypt
import jwt
from flask_jwt import JWT, jwt_required
import datetime
from datetime import datetime as ddt
from models import db
from models.user import User
# from flask_login import login_required, current_user
from models.missing_person import MissingPerson
from werkzeug.security import check_password_hash
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app = Flask(__name__)

# Set the JWT secret key
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

# Set the JWT realm
app.config['JWT_DEFAULT_REALM'] = 'login required'

# Other JWT configuration options can be set as needed
# app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=2)
# ...


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)


def authenticate(username, password):
    # Find the user in the database based on the provided username
    user = User.query.filter_by(username=username).first()

    # If user exists and the password is correct, return the user object
    if user and check_password_hash(user.password, password):
        return user


def identity(payload):
    # Extract the user ID from the payload
    user_id = payload['identity']

    # Find the user in the database based on the user ID
    user = User.query.get(user_id)

    return user


# Initialize the JWT extension
# jwt = JWT(app, authenticate, identity)


@app.route('/')
def hello():
    return jsonify('Hello, Flask!')


####################################################################
@app.route('/api/v1/login', methods=['POST'])
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
    expiration = datetime.datetime.utcnow(
    ) + datetime.timedelta(hours=2)  # Token expires in 2 hours

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


@app.route('/api/v1/signup', methods=['POST'])
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
    new_user = User(username=username, password=hashed_password,
                    email=email,  full_name=full_name, phone_number=phone_number)

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


# ################################################################3
@app.route('/api/v1/missing-persons', methods=['GET'])
# @jwt_required()
def get_missing_persons():
    # Implement logic to retrieve missing person records
    missing_persons = MissingPerson.query.all()

    # Return the missing person records as a JSON response
    result = []
    for person in missing_persons:
        result.append({
            'id': person.id,
            'name': person.name,
            'age': person.age,
            'gender': person.gender,
            'image': person.image,
            'description': person.description,
            'lastKnownLocation': person.lastKnownLocation,
            'dateOfDisappearance': person.dateOfDisappearance.strftime('%Y-%m-%d')
        })

    return jsonify(result), 200

# ##############################################################################


@app.route('/api/v1/missing-persons', methods=['POST'])
# @jwt_required()
def create_missing_person():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    # Retrieve the missing person data from the request
    print(request.json.get('name'))
    print(request.json.get('name'))
    print(request.files.get('image'))
    print(request.form.get('image'))
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    name = request.json.get('name')
    age = request.json.get('age')
    gender = request.json.get('gender')
    image = request.files.get('image')
    description = request.json.get('description')
    last_known_location = request.json.get('lastKnownLocation')
    image = "john_caviziel.png"

    # Validate the missing person data (check if required fields are present)

    # Create a new missing person record
    missing_person = MissingPerson(
        name=name,
        age=age,
        gender=gender,
        description=description,
        lastKnownLocation=last_known_location,
        image=image
    )

    # Save the image using the missing person's ID
    missing_person.save_image(image)

    # Add the missing person record to the database
    db.session.add(missing_person)
    db.session.commit()

    return jsonify(message='Missing person record created successfully'), 201


# Create all tables and flush the users table
with app.app_context():
    db.create_all()
    db.session.commit()

#
# with app.app_context():
#     def create_missing_person(name, age, gender, image, description, lastKnownLocation, dateOfDisappearance):
#         missing_person = MissingPerson(
#             name=name,
#             age=age,
#             gender=gender,
#             image=image,
#             description=description,
#             lastKnownLocation=lastKnownLocation,
#             dateOfDisappearance=dateOfDisappearance
#         )
#         db.session.add(missing_person)
#         db.session.commit()
#
#     missing_persons = [
#         {
#             'name': 'John Doe',
#             'age': 30,
#             'gender': 'Male',
#             'image': 'john_doe.jpg',
#             'description': 'Tall and slender, brown hair',
#             'lastKnownLocation': 'City A',
#             'dateOfDisappearance': ddt(2023, 5, 25)
#         },
#         {
#             'name': 'Jane Smith',
#             'age': 25,
#             'gender': 'Female',
#             'image': 'jane_smith.jpg',
#             'description': 'Short and petite, blonde hair',
#             'lastKnownLocation': 'City B',
#             'dateOfDisappearance': ddt(2023, 5, 24)
#         },
#         # Add more missing persons here
#     ]
#
#     for person in missing_persons:
#         create_missing_person(**person)
#
#     print("Missing persons added successfully.")
#

# db.init_app(app)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run()
