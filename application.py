from flask import Flask

from routes.subject_route import subject_bp
from routes.student_route import student_bp
from routes.home_route import home_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(subject_bp, url_prefix="/subject")
app.register_blueprint(student_bp, url_prefix="/student")

if __name__ == "__main__":
    app.run(debug=True)
