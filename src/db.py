import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_redshift_connection():
    redshift_url = os.getenv('REDSHIFT_URL')
    if redshift_url is None:
        raise ValueError('REDSHIFT_URL environment variable not set')
    engine = create_engine(redshift_url)
    return engine.connect()
