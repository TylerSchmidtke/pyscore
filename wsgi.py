from app import create_app
import os

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
    app.run(host='127.0.0.1')