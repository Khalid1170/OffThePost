# models.py
from datetime import datetime
from sqlalchemy import UniqueConstraint, CheckConstraint
from app import db

# --- Association: Users <-> Groups ---
class GroupMembership(db.Model):
    __tablename__ = "group_memberships"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)


# --- Core: Users ---
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    # Auth fields (keep simple for now; you can add password hashing later)
    name = db.Column(db.String(120), nullable=False, unique=True)

    # Profile fields
    fav_team = db.Column(db.String(120))
    preferred_position = db.Column(db.String(50))  # e.g., FWD/MID/DEF/GK or text
    preferred_foot = db.Column(db.String(20))      # Left/Right/Both
    nickname = db.Column(db.String(120))
    profile_pic = db.Column(db.String(255))        # optional URL/path

    memberships = db.relationship(
        "GroupMembership", backref="user", cascade="all, delete-orphan"
    )

    # Participation in session teams via SessionTeamMembership
    session_team_memberships = db.relationship(
        "SessionTeamMembership", backref="user", cascade="all, delete-orphan"
    )

    # Goals (as scorer) and assists (nullable)
    goals = db.relationship("Goal", foreign_keys="Goal.scorer_id", backref="scorer")
    assists = db.relationship("Goal", foreign_keys="Goal.assist_id", backref="assistant")

    # MVP votes (as voter and as candidate)
    mvp_votes_cast = db.relationship("MvpVote", foreign_keys="MvpVote.voter_id", backref="voter")
    mvp_votes_received = db.relationship("MvpVote", foreign_keys="MvpVote.voted_for_id", backref="candidate")

    def __repr__(self):
        return f"<User {self.name}>"


# --- Core: Groups ---
class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False, unique=True)

    # Leader can add/remove/invite
    leader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    leader = db.relationship("User", foreign_keys=[leader_id])

    members = db.relationship(
        "GroupMembership", backref="group", cascade="all, delete-orphan"
    )

    # Sessions (weekly games)
    sessions = db.relationship("Session", backref="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group {self.name}>"


# --- Sessions (weekly games) ---
class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    # Creator of the session (any member can create)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    # Optional moderator/host that finalizes stats
    host_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    host = db.relationship("User", foreign_keys=[host_id])

    # When & where
    location = db.Column(db.String(255), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)   # scheduled kick-off
    completed_at = db.Column(db.DateTime, nullable=True)  # when session marked complete (opens MVP voting window)

    # Teams in this session (flexible number)
    teams = db.relationship("SessionTeam", backref="session", cascade="all, delete-orphan")

    # Goals logged for this session
    goals = db.relationship("Goal", backref="session", cascade="all, delete-orphan")

    # MVP votes for this session
    mvp_votes = db.relationship("MvpVote", backref="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session {self.id} Group={self.group_id} {self.start_time}>"


# --- SessionTeam (e.g., Red, Blue, Team A...) ---
class SessionTeam(db.Model):
    __tablename__ = "session_teams"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)

    name = db.Column(db.String(80), nullable=False)  # e.g., "Team A", "Red", "Blue"
    captain_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    captain = db.relationship("User", foreign_keys=[captain_id])

    members = db.relationship(
        "SessionTeamMembership", backref="session_team", cascade="all, delete-orphan"
    )

    # Optional: store team score on completion (so we can compute wins quickly)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)

    __table_args__ = (
        UniqueConstraint("session_id", "name", name="uq_team_name_per_session"),
    )

    def __repr__(self):
        return f"<SessionTeam {self.name} Session={self.session_id}>"


# --- SessionTeamMembership: which player was on which team for this session ---
class SessionTeamMembership(db.Model):
    __tablename__ = "session_team_memberships"
    id = db.Column(db.Integer, primary_key=True)
    session_team_id = db.Column(db.Integer, db.ForeignKey("session_teams.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (UniqueConstraint("session_team_id", "user_id", name="uq_player_once_per_team"),)

    def __repr__(self):
        return f"<SessionTeamMembership Team={self.session_team_id} User={self.user_id}>"


# --- Goals (with optional assist) ---
class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("session_teams.id"), nullable=False)
    team = db.relationship("SessionTeam", foreign_keys=[team_id])

    scorer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assist_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Optional: minute of goal if you want to add later
    minute = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent self-assist if you want (business rule — here as a soft check)
    __table_args__ = (
        CheckConstraint("assist_id IS NULL OR assist_id != scorer_id", name="ck_no_self_assist"),
    )

    def __repr__(self):
        return f"<Goal Session={self.session_id} Team={self.team_id} Scorer={self.scorer_id}>"


# --- MVP Votes (one vote per participant; no self-vote) ---
class MvpVote(db.Model):
    __tablename__ = "mvp_votes"
    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    voted_for_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "voter_id", name="uq_one_vote_per_session"),
        CheckConstraint("voter_id != voted_for_id", name="ck_no_self_vote"),
    )

    def __repr__(self):
        return f"<MvpVote Session={self.session_id} Voter={self.voter_id} For={self.voted_for_id}>"
