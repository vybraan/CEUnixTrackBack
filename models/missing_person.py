from datetime import datetime
from models import db
import os


class MissingPerson(db.Model):
    __tablename__ = 'missing_persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    lastKnownLocation = db.Column(db.String(100), nullable=False)
    dateOfDisappearance = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def save_image(self, image_file):
        if image_file:
            # Generate a filename based on the missing person's ID, name, and date
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{self.id}_{self.name}_{timestamp}.png"

            # Save the image file to a folder (e.g., 'images')
            image_path = os.path.join("images/people/missing", filename)
            image_file.save(image_path)

            # Update the image field in the model instance
            self.image = image_path
