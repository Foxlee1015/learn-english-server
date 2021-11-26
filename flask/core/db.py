import os

import redis
from flask_pymongo import PyMongo
from dotenv import load_dotenv

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


# def backup_db():
#     BACKUP_PATH = "/var/backups"
#     DATETIME = time.strftime("%Y%m%d_%H%M%S")
#     TODAYBACKUPPATH = f"{BACKUP_PATH}/{DATETIME}"
#     MYSQL_DB_DICRECTORY = f"/var/lib/mysql/{db_dataset}"
#     MYSQL_CONTAINER = "cook_mysql"

#     try:
#         mkdir_cmd = f"mkdir {TODAYBACKUPPATH}"
#         docker_command(MYSQL_CONTAINER, mkdir_cmd)

#         mysql_dump_cmd = f"mysqldump -u {db_user} -p{db_pw} --databases {db_dataset} > {TODAYBACKUPPATH}/{db_dataset}.sql"
#         docker_command(MYSQL_CONTAINER, mysql_dump_cmd)

#         print("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")
#     except Exception as e:
#         traceback.print_exc()
#         print("db back error : ", e)
