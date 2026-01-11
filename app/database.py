import os
import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

_db = None


def get_db():
    global _db
    if _db is None:
        cred_path = settings.google_application_credentials
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
        _db = firestore.client()
    return _db
