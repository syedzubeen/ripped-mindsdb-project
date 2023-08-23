from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Import routes at the bottom to avoid circular imports
from app import routes

# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
