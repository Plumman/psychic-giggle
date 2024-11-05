from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_CONNECTION_STRING = os.getenv(
    "DB_CONNECTION_STRING", "mysql+pymysql://root:p%40ssword@localhost:3306/testdb")

# Create the engine
engine = create_engine(DB_CONNECTION_STRING)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def execute_query(query):
    with SessionLocal() as session:
        result = session.execute(text(query))
        return result.fetchall()

# Test the connection
def test_connection():
    with engine.connect() as connection:
        result = execute_query("SELECT * FROM trips")
        for row in result:
            print(row)
