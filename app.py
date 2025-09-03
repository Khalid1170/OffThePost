# app.py
import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists (for the SQLite file)
    os.makedirs(app.instance_path, exist_ok=True)

    # DB: instance/offthepost.db
    db_path = os.path.join(app.instance_path, "offthepost.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # MVP voting window (3 hours) – you can use this later in logic
    app.config["MVP_VOTING_WINDOW"] = timedelta(hours=3)

    db.init_app(app)
    Migrate(app, db)

    # Import models so Alembic can “see” them
    from models import (
        User, Group, GroupMembership,
        Session, SessionTeam, SessionTeamMembership,
        Goal, MvpVote
    )

    @app.route("/")
    def index():
        return {"message": "OffThePost API running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
