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

from werkzeug.utils import secure_filename
import os

# Specify the allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Specify the directory where the uploaded images will be saved
UPLOAD_FOLDER = '/images/people/missing'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
app.config['JWT_DEFAULT_REALM'] = 'login required'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=36)


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
def create_missing_person():
    # Retrieve the missing person data from the request
    name = request.json.get('name')
    age = request.json.get('age')
    gender = request.json.get('gender')
    image = request.files.get('image')
    description = request.json.get('description')
    last_known_location = request.json.get('lastKnownLocation')
    date_of_disappearance = request.json.get('dateOfDisappearance')

    # Validate the missing person data (check if required fields are present)
    if not name or not age or not gender or not description or not last_known_location or not image:
        return jsonify(error='Missing required fields'), 400

    # Check if the file extension is allowed
    if not allowed_file(image.filename):
        return jsonify(error='Invalid file type'), 400

    # Generate a secure filename and save the image to the server
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    # Create a new missing person record
    missing_person = MissingPerson(
        name=name,
        age=age,
        gender=gender,
        description=description,
        lastKnownLocation=last_known_location,
        dateOfDisappearance=date_of_disappearance
    )

    # Save the image using the missing person's ID
    save_image(missing_person, image)

    # Add the missing person record to the database
    db.session.add(missing_person)
    db.session.commit()

    return jsonify(message='Missing person record created successfully'), 201


def save_image(missing_person, image_file):
    if image_file:
        # Generate a filename based on the missing person's ID, name, and date
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"{missing_person.id}_{missing_person.name}_{timestamp}.png"

        # Save the image file to a folder (e.g., 'images')
        image_path = os.path.join("images/people/missing", filename)
        image_file.save(image_path)

        # Update the image field in the missing person model instance
        missing_person.image = image_path


def allowed_file(filename):
    # Check if the file extension is allowed
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create all tables and flush the users table
with app.app_context():
    db.create_all()
    db.session.commit()


# db.init_app(app)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run()
