import datetime
import os
import pipes
import traceback
import time
from contextlib import contextmanager

import redis
import pymysql
from flask_pymongo import PyMongo
from dotenv import load_dotenv

from core import errors
from core.utils import (
    docker_command,
    stringify_given_datetime_or_current_datetime,
    generate_hashed_password,
    parse_given_str_datetime_or_current_datetime,
)


# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


mongo = PyMongo()
mongo_uri = os.getenv("MONGO_DB_URI")

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

redis_store = redis.Redis(
    host=redis_host, port=redis_port, password=redis_password, decode_responses=True
)

db_host_dev = os.getenv("DB_HOST_DEV")
db_host = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT"))
db_user = os.getenv("DB_USERNAME")
db_pw = os.getenv("DB_PASSWORD")
db_dataset = os.getenv("DB_DATABASE")
db_charset = os.getenv("DB_CHARSET")

db_info_kwargs = {
    "host": db_host_dev,
    "port": db_port,
    "user": db_user,
    "password": db_pw,
    "db": db_dataset,
    "charset": db_charset,
    "cursorclass": pymysql.cursors.DictCursor,
}


@contextmanager
def get_db():
    try:
        conn = None
        try:
            conn = pymysql.connect(**db_info_kwargs)
        except:
            # print("db host dev connect exception")
            db_info_kwargs["host"] = db_host
            conn = pymysql.connect(**db_info_kwargs)
        yield conn
    except:
        traceback.print_exc()
    finally:
        conn.close()
        pass


def init_db():
    with get_db() as conn:
        from core import schema

        sql_list = schema.schema.split(";")
        for sql in sql_list:
            if sql != "" and sql != "\n":
                try:
                    conn.cursor().execute(sql)
                except:
                    traceback.print_exc()
        conn.commit()

    _create_default_users()


def _create_default_users():

    if not get_user(name="admin"):
        ADMIN_NAME = os.getenv("ADMIN_NAME")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
        print("Created admin user")
        insert_user(ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, 0)


def backup_db():
    BACKUP_PATH = "/var/backups"
    DATETIME = time.strftime("%Y%m%d_%H%M%S")
    TODAYBACKUPPATH = f"{BACKUP_PATH}/{DATETIME}"
    MYSQL_DB_DICRECTORY = f"/var/lib/mysql/{db_dataset}"
    MYSQL_CONTAINER = "cook_mysql"

    try:
        mkdir_cmd = f"mkdir {TODAYBACKUPPATH}"
        docker_command(MYSQL_CONTAINER, mkdir_cmd)

        mysql_dump_cmd = f"mysqldump -u {db_user} -p{db_pw} --databases {db_dataset} > {TODAYBACKUPPATH}/{db_dataset}.sql"
        docker_command(MYSQL_CONTAINER, mysql_dump_cmd)

        print("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")
    except Exception as e:
        traceback.print_exc()
        print("db back error : ", e)


def insert_user(user_name, email, password, user_type):
    hashed_password, salt = generate_hashed_password(password)
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = "INSERT into user(name, email, password, salt, user_type) values (%s,%s,%s,%s,%s)"
            cur.execute(sql, (user_name, email, hashed_password, salt, user_type))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def get_user_hashed_password_with_user_id(name):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, password, salt
                FROM user
            """
            sql = add_condition_to_query(sql, "name", name)
            cur.execute(sql)
            conn.commit()
            res = cur.fetchone()
            return res
    except:
        traceback.print_exc()
        return False


def get_users():
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
            return res
    except:
        traceback.print_exc()
        return False


def get_particles(id_=None, name=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT *
                FROM particle
            """

            if id_ is not None:
                sql = add_condition_to_query(sql, "id", id_)

            elif name is not None:
                sql = add_condition_to_query(sql, "name", name)

            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
            return res
    except:
        traceback.print_exc()
        return False


def delete_particles(ids):
    try:
        with get_db() as conn:

            cur = conn.cursor()

            sql = f"""
                DELETE FROM particle
                WHERE id in ({','.join(str(id) for id in ids)})
            """
            cur.execute(sql)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def insert_particles(names=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = "INSERT IGNORE into particle(name) values (%s)"
            cur.executemany(sql, (names))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def get_user(id_=None, name=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            if id_ is not None:
                sql = add_condition_to_query(sql, "id", id_)
            elif name is not None:
                sql = add_condition_to_query(sql, "name", name)

            cur.execute(sql)
            conn.commit()
            res = cur.fetchone()

            return res
    except:
        traceback.print_exc()
        return False


def delete_users(user_ids):
    """
    :param user_ids: a list of user ids
    """
    try:
        with get_db() as conn:

            cur = conn.cursor()

            sql = f"""
                DELETE FROM user
                WHERE id in ({','.join(str(user_id) for user_id in user_ids)})
            """
            cur.execute(sql)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def add_condition_to_query(sql, col, row, is_first_condition=True):
    if is_first_condition:
        sql += " WHERE "
    else:
        sql += " AND "
    if isinstance(row, int):
        sql += f" {col}={row}"
    elif isinstance(row, str):
        sql += f" {col}='{row}'"
    return sql


def add_multiple_conditions_to_query(sql, cols_rows):
    sql += " WHERE"
    for col_row in cols_rows:
        col = col_row["col"]
        row = col_row["row"]
        if isinstance(col_row["col"], int):
            sql += f" {col}={row}"
        else:
            sql += f" {col}='{row}'"
