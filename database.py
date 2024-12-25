from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']


engine = create_engine(db_connection_string)

Session = sessionmaker(bind=engine)

# Function to get a session
def get_session():
    return Session()
