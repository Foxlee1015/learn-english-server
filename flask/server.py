import sys
from app import create_app

if __name__ == "__main__":
    config_name = sys.argv[1]
    app = create_app(config_name)
    app.run(
        host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"]
    )
