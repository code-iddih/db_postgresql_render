#!/usr/bin/env python3

import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from models import db, User, Entry, Photo, Tag, EntryTag
from app import app

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample users
        user1 = User(
            username='john_doe',
            email='john@example.com',
            password_hash=generate_password_hash('password123'),
            created_at=datetime.now(timezone.utc)
        )
        
        user2 = User(
            username='jane_doe',
            email='jane@example.com',
            password_hash=generate_password_hash('password456'),
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Create sample entries
        entry1 = Entry(
            location='New York, NY',
            date=datetime.now(timezone.utc),
            description='Visited Central Park.',
            user_id=user1.id,
            created_at=datetime.now(timezone.utc)
        )

        entry2 = Entry(
            location='San Francisco, CA',
            date=datetime.now(timezone.utc),
            description='Saw the Golden Gate Bridge.',
            user_id=user2.id,
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()

        # Create sample photos
        photo1 = Photo(
            url='https://example.com/photo1.jpg',
            entry_id=entry1.id,
            uploaded_at=datetime.now(timezone.utc)
        )

        photo2 = Photo(
            url='https://example.com/photo2.jpg',
            entry_id=entry2.id,
            uploaded_at=datetime.now(timezone.utc)
        )

        db.session.add(photo1)
        db.session.add(photo2)
        db.session.commit()

        # Create sample tags
        tag1 = Tag(name='Travel', created_at=datetime.now(timezone.utc))
        tag2 = Tag(name='Nature', created_at=datetime.now(timezone.utc))

        db.session.add(tag1)
        db.session.add(tag2)
        db.session.commit()

        # Associate tags with entries
        entry_tag1 = EntryTag(entry_id=entry1.id, tag_id=tag1.id)
        entry_tag2 = EntryTag(entry_id=entry2.id, tag_id=tag2.id)

        db.session.add(entry_tag1)
        db.session.add(entry_tag2)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
