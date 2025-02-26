from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
def create_collections_with_validation_admin():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['face_recognition']
    admin_schema={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                }
           }
       }
    }
    try:
        db.create_collection("admins", validator=admin_schema)
    except CollectionInvalid:
        print("Collection 'admin' already exists. Skipping creation.")
    return db
if __name__ == "__main__":
    create_collections_with_validation_admin()
