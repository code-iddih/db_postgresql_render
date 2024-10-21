#!/usr/bin/env python3

from flask import Flask, jsonify, request, render_template 
from flask_migrate import Migrate
from models import db, User, Entry, Photo, Tag 
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from pathlib import Path

dotenv_path = Path(__file__).resolve().parent / '.env'


# Loading the .env file
load_dotenv(dotenv_path)

# Creating Flask app instance
app = Flask(
    __name__,
    static_url_path='',
    static_folder='../client/build',
    template_folder='../client/build'
)


# Enables CORS for all routes
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")
app.json.compact = False 

# Initializing Flask-Migrate and JWT Manager
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initializing the database with the app context
db.init_app(app)

# Home
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API! Use the /api endpoint for more information."}), 200

# User registration
@app.route('/api/users/register', methods=['POST'])
def user_register():
    data = request.get_json()
    print("Received data:", data)  # Log incoming data

    if not data or not all(key in data for key in ('username', 'email', 'password_hash')):
        print("Missing required fields")  # Log error
        return jsonify({"error": "Missing required fields"}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password_hash']),  # Hashing the password
        created_at=datetime.utcnow()  # Set the joined date
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# User login
@app.route('/api/users/login', methods=['POST'])
def user_login():
    data = request.get_json()
    if not data or not all(key in data for key in ('username', 'password')):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

# Password reset request (placeholder)
@app.route('/api/users/reset-password', methods=['POST'])
def user_reset_password():
    data = request.get_json()
    return jsonify({"message": "Password reset request received"}), 200

# User profile
@app.route('/api/users/profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)  # Use session.get()

    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "joined": user.created_at.strftime('%Y-%m-%d %H:%M:%S')  
    }
    
    return jsonify(user_data), 200

# Retrieve all entries
@app.route('/api/entries', methods=['GET', 'POST'])
@jwt_required(optional=True)
def entry_list():
    if request.method == 'GET':
        entries = Entry.query.all()
        entries_list = [
            {
                "id": entry.id,
                "location": str(entry.location), 
                "date": entry.date.strftime('%Y-%m-%d %H:%M:%S') if entry.date else None,
                "description": str(entry.description), 
                "user_id": entry.user_id
            } for entry in entries
        ]
        return jsonify(entries_list), 200

    if request.method == 'POST':
        data = request.get_json()
        
        # Use only the date format
        try:
            entry_date = datetime.strptime(data.get('date'), '%Y-%m-%d')  
        except ValueError:
            return jsonify({"error": "Invalid date format. Use 'YYYY-MM-DD'."}), 400

        new_entry = Entry(
            location=data.get('location'),
            date=entry_date,
            description=data.get('description'),
            user_id=get_jwt_identity()
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"id": new_entry.id}), 201

# Retrieve a specific entry
@app.route('/api/entries/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required(optional=True)
def entry_resource(id):
    entry = db.session.get(Entry, id)

    if request.method == 'GET':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404

        entry_data = {
            "id": entry.id,
            "location": entry.location,
            "date": entry.date.strftime('%Y-%m-%d %H:%M:%S'),
            "description": entry.description,
            "user_id": entry.user_id
        }
        return jsonify(entry_data), 200

    if request.method == 'PUT':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404
        
        data = request.get_json()
        entry.location = data.get('location', entry.location)

        # Update date with parsing
        date_str = data.get('date', entry.date.strftime('%Y-%m-%d %H:%M:%S'))
        try:
            entry.date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            entry.date = datetime.strptime(date_str, '%Y-%m-%d')  

        entry.description = data.get('description', entry.description)

        db.session.commit()
        return jsonify({"message": "Entry updated successfully"}), 200

    if request.method == 'DELETE':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404
        
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Entry deleted successfully"}), 200

# Deleting a photo  
@app.route('/api/entries/<int:entry_id>/photos/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(entry_id, photo_id):
    photo = Photo.query.filter_by(id=photo_id, entry_id=entry_id).first()
    if photo is None:
        return jsonify({"error": "Photo not found"}), 404

    db.session.delete(photo)
    db.session.commit()
    return jsonify({"message": "Photo deleted successfully"}), 200

# Retrieve all photos for an entry
@app.route('/api/entries/<int:id>/photos', methods=['GET', 'POST'])
@jwt_required()
def entry_photos(id):
    entry = db.session.get(Entry, id)
    
    if request.method == 'GET':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404
        
        photos = Photo.query.filter_by(entry_id=id).all()
        photos_list = [{"id": photo.id, "url": photo.url} for photo in photos]
        return jsonify(photos_list), 200

    if request.method == 'POST':
        data = request.get_json()
        
        if 'url' not in data or not data['url']:
            return jsonify({"error": "Photo URL is required."}), 400

        new_photo = Photo(
            url=data['url'],  
            entry_id=id,
            uploaded_at=datetime.utcnow()
        )

        db.session.add(new_photo)

        try:
            db.session.commit()
            return jsonify({"id": new_photo.id, "url": new_photo.url}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to upload photo: {str(e)}"}), 500
        
# Tags management
@app.route('/api/tags', methods=['GET'])
@jwt_required()
def get_tags():
    tags = Tag.query.all()
    return jsonify([{'id': tag.id, 'name': tag.name, 'created_at': tag.created_at.isoformat()} for tag in tags])
@app.route('/api/tags', methods=['POST'])
@jwt_required()
def create_tag():
    data = request.json
    existing_tag = Tag.query.filter_by(name=data['name']).first()
    if existing_tag:
        return jsonify({"id": existing_tag.id, "name": existing_tag.name})
    new_tag = Tag(name=data['name'])
    db.session.add(new_tag)
    db.session.commit()
    return jsonify({"id": new_tag.id, "name": new_tag.name}), 201

@app.route('/api/entries/<int:entry_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    data = request.json
    tag = Tag.query.get_or_404(data['tag_id'])
    if tag not in entry.tags:
        entry.tags.append(tag)
        db.session.commit()
    return jsonify({"message": "Tag added successfully"}), 200

@app.route('/api/entries/<int:entry_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_entry(entry_id, tag_id):
    entry = Entry.query.get_or_404(entry_id)
    tag = Tag.query.get_or_404(tag_id)
    if tag in entry.tags:
        entry.tags.remove(tag)
        db.session.commit()
    return '', 204

@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return '', 204

# Update user profile
@app.route('/api/users/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)  # Use session.get()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    # Updating the user's username if provided
    if 'username' in data:
        user.username = data['username']

    db.session.commit()

    return jsonify({"message": "User profile updated successfully"}), 200

# Running the application
if __name__ == '__main__':
    app.run(debug = False)
