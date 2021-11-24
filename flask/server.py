import sys
from app import create_app, set_db

if __name__ == "__main__":
    config_name = sys.argv[1]
    if config_name in ["prod", "dev", "test"]:
        app = create_app(config_name)
        set_db(app)
        app.run(
            host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"]
        )
    else:
        print("Provide a config name(one of prod, dev or test)")
