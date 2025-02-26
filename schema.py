from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

def create_collections_with_validation():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['face_recognition']
    
    # Define the schema validation
    user_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_name", "rollno", "registration_no"],
            "properties": {
                "user_name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "rollno": {
                    "bsonType": "int",
                    "description": "must be an integer and is required"
                },
                "branch":{
                    "bsonType":"string",
                    "description":"must be a string and is required"
                },
                "registration_no": {
                    "bsonType": "int",
                    "description": "must be an integer and is required"
                },
                "bio":{
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
            }
        }
    }
    try:
        db.create_collection("users", validator=user_schema)
    except CollectionInvalid:
        print("Collection 'users' already exists. Skipping creation.")
    # Create unique indexes
    db.users.create_index("user_name", unique=True)
    db.users.create_index("rollno", unique=True)

    return db

# Call the function to create collections with validation
if __name__ == "__main__":
    create_collections_with_validation()
