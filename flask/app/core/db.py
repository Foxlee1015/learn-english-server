import os
from flask_pymongo import PyMongo

mongo = PyMongo()


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
