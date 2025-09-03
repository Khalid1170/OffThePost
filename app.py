# app.py
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from db import db

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

    # --- User Routes ---
    @app.route("/users", methods=["GET"])
    def get_users():
        users = User.query.all()
        return jsonify([{
            "id": u.id,
            "name": u.name,
            "fav_team": u.fav_team,
            "preferred_position": u.preferred_position,
            "preferred_foot": u.preferred_foot,
            "nickname": u.nickname,
            "goals_scored": u.goals_scored_count,
            "assists": u.assists_count,
            "mvp_wins": u.mvp_wins_count,
            "teams_played": [f"{t.name} ({t.session.group.name})" for t in u.teams_played]
        } for u in users])

    @app.route("/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify({
            "id": user.id,
            "name": user.name,
            "fav_team": user.fav_team,
            "preferred_position": user.preferred_position,
            "preferred_foot": user.preferred_foot,
            "nickname": user.nickname,
            "goals_scored": user.goals_scored_count,
            "assists": user.assists_count,
            "mvp_wins": user.mvp_wins_count,
            "teams_played": [f"{t.name} ({t.session.group.name})" for t in user.teams_played]
        })

    @app.route("/users", methods=["POST"])
    def create_user():
        data = request.get_json()
        user = User(
            name=data["name"],
            fav_team=data.get("fav_team"),
            preferred_position=data.get("preferred_position"),
            preferred_foot=data.get("preferred_foot"),
            nickname=data.get("nickname")
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "message": "User created"}), 201

    # --- Group Routes ---
    @app.route("/groups", methods=["GET"])
    def get_groups():
        groups = Group.query.all()
        return jsonify([{
            "id": g.id,
            "name": g.name,
            "leader": g.leader.name if g.leader else None
        } for g in groups])

    @app.route("/groups", methods=["POST"])
    def create_group():
        data = request.get_json()
        group = Group(name=data["name"])
        db.session.add(group)
        db.session.commit()
        return jsonify({"id": group.id, "message": "Group created"}), 201

    # --- Session Routes ---
    @app.route("/sessions", methods=["GET"])
    def get_sessions():
        sessions = Session.query.all()
        return jsonify([{
            "id": s.id,
            "group": s.group.name,
            "location": s.location,
            "start_time": s.start_time.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        } for s in sessions])

    @app.route("/sessions", methods=["POST"])
    def create_session():
        data = request.get_json()
        session = Session(
            group_id=data["group_id"],
            location=data.get("location"),
            start_time=datetime.fromisoformat(data["start_time"])
        )
        db.session.add(session)
        db.session.commit()
        return jsonify({"id": session.id, "message": "Session created"}), 201

    # --- Session Team Routes ---
    @app.route("/session_teams", methods=["GET"])
    def get_session_teams():
        teams = SessionTeam.query.all()
        return jsonify([{"id": t.id, "session_id": t.session_id, "name": t.name, "captain_id": t.captain_id} for t in teams])

    @app.route("/session_teams", methods=["POST"])
    def create_session_team():
        data = request.get_json()
        team = SessionTeam(
            session_id=data["session_id"],
            name=data["name"],
            captain_id=data.get("captain_id")
        )
        db.session.add(team)
        db.session.commit()
        return jsonify({"id": team.id, "message": "Team created"}), 201

    # --- Goal Routes ---
    @app.route("/goals", methods=["GET"])
    def get_goals():
        goals = Goal.query.all()
        return jsonify([{
            "id": g.id,
            "session_id": g.session_id,
            "team_id": g.team_id,
            "scorer_id": g.scorer_id,
            "assist_id": g.assist_id,
            "minute": g.minute
        } for g in goals])

    @app.route("/goals", methods=["POST"])
    def create_goal():
        data = request.get_json()
        goal = Goal(
            session_id=data["session_id"],
            team_id=data["team_id"],
            scorer_id=data["scorer_id"],
            assist_id=data.get("assist_id"),
            minute=data.get("minute")
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({"id": goal.id, "message": "Goal logged"}), 201

    # --- MVP Vote Routes ---
    @app.route("/mvp_votes", methods=["GET"])
    def get_mvp_votes():
        votes = MvpVote.query.all()
        return jsonify([{
            "id": v.id,
            "session_id": v.session_id,
            "voter_id": v.voter_id,
            "voted_for_id": v.voted_for_id,
            "created_at": v.created_at.isoformat()
        } for v in votes])

    @app.route("/mvp_votes", methods=["POST"])
    def create_mvp_vote():
        data = request.get_json()
        vote = MvpVote(
            session_id=data["session_id"],
            voter_id=data["voter_id"],
            voted_for_id=data["voted_for_id"]
        )
        db.session.add(vote)
        db.session.commit()
        return jsonify({"id": vote.id, "message": "Vote cast"}), 201

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
