import os
import requests
import random
from datetime import datetime, timedelta
import uuid

boundary = uuid.uuid4().hex


api_url = 'http://192.168.8.176:5099/api'

headers = {
    "Content-Type": "application/json"
}


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
            date_of_disappearance_str = date_of_disappearance.isoformat()
            data = {
                'name': name,
                'age': age,
                'gender': gender,
                'description': description,
                'lastKnownLocation': last_known_location,
                'date_of_disappearance': date_of_disappearance_str,
                'image': " "
            }

            #files = {'image': image_file}

            response = requests.post(
                api_url + '/MissingPersons', headers=headers, json=data)
            if response.status_code == 201:
                print('Missing person seeded successfully')
            else:
                print('Failed to seed missing person')
                print(response.text)

        os.remove(image_path)  # Delete the temporary image file




first_names = [
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    "Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"
]


# Generate and seed missing person information 10 times
for _ in range(10):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f'{first_name} {last_name}'

    age = random.randint(10, 40)
    genders = ['Male', 'Female']
    gender = random.choice(genders)
    image_url = retrieve_image_url(gender)
    description = 'Description of the missing person'
    last_known_location = 'City'
    date_of_disappearance = datetime.now() - timedelta(days=random.randint(1, 30))

    seed_missing_person(name, age, gender, image_url,
                        description, last_known_location, date_of_disappearance)

