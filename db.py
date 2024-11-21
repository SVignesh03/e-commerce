from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the connection string and database name from the environment
mongo_uri = os.getenv("MONGO_URI")
mongo_db_name = os.getenv("MONGO_DB_NAME")

# MongoDB connection
try:
    client = MongoClient(mongo_uri)
    conn = client[mongo_db_name]  # This is your MongoDB database
    print("MongoDB connection established successfully.")
except Exception as e:
    print("Error connecting to MongoDB:", e)
