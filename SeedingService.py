import os
import requests
import random
from datetime import datetime, timedelta

api_url = 'http://localhost:5000/api/v1'


def retrieve_image_url(gender):
    if gender.lower() == 'male':
        url = f'https://randomuser.me/api/portraits/men/{random.randint(10, 20)}.jpg'
    else:
        url = f'https://randomuser.me/api/portraits/women/{random.randint(10, 20)}.jpg'
    return url


def seed_missing_person(name, age, gender, image_url, description, last_known_location, date_of_disappearance):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_filename = f'{name.replace(" ", "_")}.jpg'
        image_path = os.path.join(os.path.abspath('.'), image_filename)
        with open(image_path, 'wb') as image_file:
            image_file.write(response.content)

        with open(image_path, 'rb') as image_file:
            data = {
                'name': name,
                'age': age,
                'gender': gender,
                'description': description,
                'last_known_location': last_known_location,
                'date_of_disappearance': date_of_disappearance
            }

            files = {'image': image_file}

            response = requests.post(
                api_url + '/missing-persons', data=data, files=files)
            if response.status_code == 200:
                print('Missing person seeded successfully')
            else:
                print('Failed to seed missing person')
                print(response.text)

        os.remove(image_path)  # Delete the temporary image file


# Generate and seed missing person information 10 times
for _ in range(10):
    names = ['John Doe', 'Jane Smith', 'Michael Johnson', 'Emily Davis']
    age = random.randint(20, 60)
    genders = ['Male', 'Female']
    gender = random.choice(genders)
    image_url = retrieve_image_url(gender)
    description = 'Description of the missing person'
    last_known_location = 'City'
    date_of_disappearance = datetime.now() - timedelta(days=random.randint(1, 30))

    seed_missing_person(random.choice(names), age, gender, image_url,
                        description, last_known_location, date_of_disappearance)
