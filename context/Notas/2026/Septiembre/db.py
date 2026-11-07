Import os
from contextlib import contextmanager
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


def get_conninfo():
    return (
        f"host={os.getenv('DB_HOST', 'localhost')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'tienda')} "
        f"user={os.getenv('DB_USER', 'postgres')} "
        f"password={os.getenv('DB_PASSWORD', '')}"
    )


def get_connection():
    return psycopg.connect(get_conninfo(), row_factory=dict_row)