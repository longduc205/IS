import pymysql
from flask import current_app


def get_db_connection():
    """Get a raw database connection for vulnerable demos."""
    return pymysql.connect(
        host=current_app.config["DATABASE_HOST"],
        port=current_app.config["DATABASE_PORT"],
        user=current_app.config["DATABASE_USER"],
        password=current_app.config["DATABASE_PASSWORD"],
        database=current_app.config["DATABASE_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
