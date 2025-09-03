# seed.py
from datetime import datetime, timedelta, timezone
from app import create_app, db
from models import (
    User, Group, GroupMembership,
    Session, SessionTeam, SessionTeamMembership,
    Goal, MvpVote
)

app = create_app()

def add_members(group, names, users_cache):
    """Create users if missing, add membership to group."""
    memberships = []
    # Sample attributes for users
    user_attrs = {
        "Khalid": {"fav_team": "Arsenal", "preferred_position": "FWD", "preferred_foot": "Right", "nickname": "Khal"},
        "Mohamed": {"fav_team": "Chelsea", "preferred_position": "MID", "preferred_foot": "Left", "nickname": "Mo"},
        "Mubarak": {"fav_team": "Liverpool", "preferred_position": "DEF", "preferred_foot": "Right", "nickname": "Mub"},
        "Khadar": {"fav_team": "Manchester United", "preferred_position": "GK", "preferred_foot": "Both", "nickname": "Kad"},
        "Abdi": {"fav_team": "Barcelona", "preferred_position": "FWD", "preferred_foot": "Left", "nickname": "Abd"},
        "Yaya": {"fav_team": "Real Madrid", "preferred_position": "MID", "preferred_foot": "Right", "nickname": "Yay"},
        "Ilyas": {"fav_team": "Bayern Munich", "preferred_position": "DEF", "preferred_foot": "Both", "nickname": "Ily"},
        "Ismail": {"fav_team": "PSG", "preferred_position": "GK", "preferred_foot": "Right", "nickname": "Ism"},
        "Malik": {"fav_team": "Juventus", "preferred_position": "FWD", "preferred_foot": "Left", "nickname": "Mal"},
        "Hamsa": {"fav_team": "AC Milan", "preferred_position": "MID", "preferred_foot": "Right", "nickname": "Ham"},
        "Yusuf": {"fav_team": "Inter Milan", "preferred_position": "DEF", "preferred_foot": "Both", "nickname": "Yus"},
        "Sayid": {"fav_team": "Napoli", "preferred_position": "GK", "preferred_foot": "Left", "nickname": "Say"},
        "Ahmed": {"fav_team": "Tottenham", "preferred_position": "FWD", "preferred_foot": "Right", "nickname": "Ahd"},
        "Bilal": {"fav_team": "Leicester", "preferred_position": "MID", "preferred_foot": "Left", "nickname": "Bil"},
        "Farah": {"fav_team": "Everton", "preferred_position": "DEF", "preferred_foot": "Both", "nickname": "Far"},
        "Samir": {"fav_team": "West Ham", "preferred_position": "GK", "preferred_foot": "Right", "nickname": "Sam"},
        "Omar": {"fav_team": "Newcastle", "preferred_position": "FWD", "preferred_foot": "Left", "nickname": "Oma"},
        "Karim": {"fav_team": "Aston Villa", "preferred_position": "MID", "preferred_foot": "Right", "nickname": "Kar"},
        "Taha": {"fav_team": "Wolves", "preferred_position": "DEF", "preferred_foot": "Both", "nickname": "Tah"},
        "Zak": {"fav_team": "Southampton", "preferred_position": "GK", "preferred_foot": "Left", "nickname": "Zak"},
    }
    for n in names:
        user = users_cache.get(n) or User.query.filter_by(name=n).first()
        if not user:
            attrs = user_attrs.get(n, {})
            user = User(
                name=n,
                fav_team=attrs.get("fav_team"),
                preferred_position=attrs.get("preferred_position"),
                preferred_foot=attrs.get("preferred_foot"),
                nickname=attrs.get("nickname"),
                profile_pic=None,  # Keep as None for now
            )
            db.session.add(user)
            db.session.flush()  # Flush new user
            users_cache[n] = user
        else:
            db.session.flush()  # Flush existing user if needed
        memberships.append(GroupMembership(user=user, group=group))
    db.session.add_all(memberships)
    return [m.user for m in memberships]

with app.app_context():
    db.drop_all()
    db.create_all()

    users_cache = {}

    # --- Groups ---
    g_hidden = Group(name="Hidden Leaf")
    g_boys = Group(name="The Boys")
    g_invinc = Group(name="Invincibles")
    g_stranger = Group(name="Stranger Ballers")
    g_diggers = Group(name="Goal Diggers")
    db.session.add_all([g_hidden, g_boys, g_invinc, g_stranger, g_diggers])
    db.session.flush()  # Flush to make groups in session

    # Assign leaders (just first added member later)
    # --- Members ---
    hidden_players = add_members(g_hidden, ["Khalid", "Mohamed", "Mubarak", "Khadar"], users_cache)
    boys_players = add_members(g_boys, ["Abdi", "Yaya", "Ilyas", "Ismail"], users_cache)
    inv_players = add_members(g_invinc, ["Malik", "Hamsa", "Yusuf", "Sayid"], users_cache)
    stranger_players = add_members(g_stranger, ["Ahmed", "Bilal", "Farah", "Samir"], users_cache)
    digger_players = add_members(g_diggers, ["Omar", "Karim", "Taha", "Zak"], users_cache)
    db.session.flush()  # Flush to make users in session

    # Leaders = first member of each for now
    g_hidden.leader_id = hidden_players[0].id
    g_boys.leader_id = boys_players[0].id
    g_invinc.leader_id = inv_players[0].id
    g_stranger.leader_id = stranger_players[0].id
    g_diggers.leader_id = digger_players[0].id
    db.session.commit()

    # --- Sessions (with location/time) ---
    # Past sessions for more stats
    s_hidden_past = Session(
        group=g_hidden,
        created_by=hidden_players[0],
        host=hidden_players[0],  # Khalid
        location="City Sports Hall",
        start_time=datetime(2025, 8, 21, 18, 30),
        completed_at=datetime(2025, 8, 21, 20, 30)  # Completed
    )
    s_boys_past = Session(
        group=g_boys,
        created_by=boys_players[1],
        host=boys_players[1],    # Yaya
        location="Riverside Pitch",
        start_time=datetime(2025, 8, 25, 19, 0),
        completed_at=datetime(2025, 8, 25, 21, 0)  # Completed
    )

    # Current sessions
    s_hidden = Session(
        group=g_hidden,
        created_by=hidden_players[0],
        host=hidden_players[0],  # Khalid
        location="City Sports Hall",
        start_time=datetime(2025, 8, 28, 18, 30)
    )
    s_boys = Session(
        group=g_boys,
        created_by=boys_players[1],
        host=boys_players[1],    # Yaya
        location="Riverside Pitch",
        start_time=datetime(2025, 9, 1, 19, 0)
    )
    s_inv = Session(
        group=g_invinc,
        created_by=inv_players[0],
        host=inv_players[0],     # Malik
        location="Academy 5-a-side",
        start_time=datetime(2025, 9, 5, 20, 0)
    )
    db.session.add_all([s_hidden_past, s_boys_past, s_hidden, s_boys, s_inv])
    db.session.flush()  # Flush to make sessions in session

    # --- Teams per session (flexible names) ---
    # Past Hidden Leaf session teams
    hl_past_team_a = SessionTeam(session=s_hidden_past, name="Team A", captain=hidden_players[0])  # Khalid
    hl_past_team_b = SessionTeam(session=s_hidden_past, name="Team B", captain=hidden_players[1])  # Mohamed
    db.session.add_all([hl_past_team_a, hl_past_team_b])
    db.session.flush()
    db.session.add_all([
        SessionTeamMembership(session_team=hl_past_team_a, user=hidden_players[0]),  # Khalid
        SessionTeamMembership(session_team=hl_past_team_a, user=hidden_players[2]),  # Mubarak
        SessionTeamMembership(session_team=hl_past_team_b, user=hidden_players[1]),  # Mohamed
        SessionTeamMembership(session_team=hl_past_team_b, user=hidden_players[3]),  # Khadar
    ])

    # Past The Boys session teams
    boys_past_red = SessionTeam(session=s_boys_past, name="Red", captain=boys_players[0])   # Abdi
    boys_past_blue = SessionTeam(session=s_boys_past, name="Blue", captain=boys_players[1]) # Yaya
    db.session.add_all([boys_past_red, boys_past_blue])
    db.session.flush()
    db.session.add_all([
        SessionTeamMembership(session_team=boys_past_red, user=boys_players[0]),   # Abdi
        SessionTeamMembership(session_team=boys_past_red, user=boys_players[2]),   # Ilyas
        SessionTeamMembership(session_team=boys_past_blue, user=boys_players[1]),  # Yaya
        SessionTeamMembership(session_team=boys_past_blue, user=boys_players[3]),  # Ismail
    ])

    # Current Hidden Leaf session teams: Team A / Team B with captains
    hl_team_a = SessionTeam(session=s_hidden, name="Team A", captain=hidden_players[0])  # Khalid
    hl_team_b = SessionTeam(session=s_hidden, name="Team B", captain=hidden_players[1])  # Mohamed
    db.session.add_all([hl_team_a, hl_team_b])
    db.session.flush()

    # Add members to teams
    db.session.add_all([
        SessionTeamMembership(session_team=hl_team_a, user=hidden_players[0]),  # Khalid
        SessionTeamMembership(session_team=hl_team_a, user=hidden_players[2]),  # Mubarak
        SessionTeamMembership(session_team=hl_team_b, user=hidden_players[1]),  # Mohamed
        SessionTeamMembership(session_team=hl_team_b, user=hidden_players[3]),  # Khadar
    ])

    # The Boys: Red / Blue
    boys_red = SessionTeam(session=s_boys, name="Red", captain=boys_players[0])   # Abdi
    boys_blue = SessionTeam(session=s_boys, name="Blue", captain=boys_players[1]) # Yaya
    db.session.add_all([boys_red, boys_blue])
    db.session.flush()
    db.session.add_all([
        SessionTeamMembership(session_team=boys_red, user=boys_players[0]),   # Abdi
        SessionTeamMembership(session_team=boys_red, user=boys_players[2]),   # Ilyas
        SessionTeamMembership(session_team=boys_blue, user=boys_players[1]),  # Yaya
        SessionTeamMembership(session_team=boys_blue, user=boys_players[3]),  # Ismail
    ])

    # Invincibles: Team X / Team Y
    inv_x = SessionTeam(session=s_inv, name="Team X", captain=inv_players[0])  # Malik
    inv_y = SessionTeam(session=s_inv, name="Team Y", captain=inv_players[2])  # Yusuf
    db.session.add_all([inv_x, inv_y])
    db.session.flush()
    db.session.add_all([
        SessionTeamMembership(session_team=inv_x, user=inv_players[0]),  # Malik
        SessionTeamMembership(session_team=inv_x, user=inv_players[3]),  # Sayid
        SessionTeamMembership(session_team=inv_y, user=inv_players[2]),  # Yusuf
        SessionTeamMembership(session_team=inv_y, user=inv_players[1]),  # Hamsa
    ])
    db.session.flush()  # Flush to make teams and memberships in session

    # --- Goals (example stats) ---
    # Past Hidden Leaf session goals
    db.session.add_all([
        Goal(session=s_hidden_past, team=hl_past_team_a, scorer_id=hidden_players[0].id, assist_id=hidden_players[2].id),  # Khalid <- Mubarak
        Goal(session=s_hidden_past, team=hl_past_team_b, scorer_id=hidden_players[1].id),                             # Mohamed (solo)
        Goal(session=s_hidden_past, team=hl_past_team_a, scorer_id=hidden_players[2].id, assist_id=hidden_players[0].id), # Mubarak <- Khalid
        Goal(session=s_hidden_past, team=hl_past_team_b, scorer_id=hidden_players[3].id),                             # Khadar
    ])

    # Past The Boys session goals
    db.session.add_all([
        Goal(session=s_boys_past, team=boys_past_red, scorer_id=boys_players[0].id, assist_id=boys_players[2].id),  # Abdi <- Ilyas
        Goal(session=s_boys_past, team=boys_past_blue, scorer_id=boys_players[1].id),                          # Yaya (solo)
        Goal(session=s_boys_past, team=boys_past_red, scorer_id=boys_players[2].id, assist_id=boys_players[0].id), # Ilyas <- Abdi
        Goal(session=s_boys_past, team=boys_past_blue, scorer_id=boys_players[3].id, assist_id=boys_players[1].id), # Ismail <- Yaya
    ])

    # Current Hidden Leaf session goals
    db.session.add_all([
        Goal(session=s_hidden, team=hl_team_a, scorer_id=hidden_players[0].id, assist_id=hidden_players[2].id),  # Khalid <- Mubarak
        Goal(session=s_hidden, team=hl_team_b, scorer_id=hidden_players[1].id),                             # Mohamed (solo)
        Goal(session=s_hidden, team=hl_team_a, scorer_id=hidden_players[0].id),                             # Khalid
    ])

    # The Boys session goals
    db.session.add_all([
        Goal(session=s_boys, team=boys_red, scorer_id=boys_players[0].id, assist_id=boys_players[2].id),  # Abdi <- Ilyas
        Goal(session=s_boys, team=boys_blue, scorer_id=boys_players[1].id, assist_id=boys_players[3].id), # Yaya <- Ismail
        Goal(session=s_boys, team=boys_red, scorer_id=boys_players[2].id),                          # Ilyas
    ])

    # Invincibles session goals
    db.session.add_all([
        Goal(session=s_inv, team=inv_x, scorer_id=inv_players[0].id),           # Malik
        Goal(session=s_inv, team=inv_y, scorer_id=inv_players[2].id),           # Yusuf
        Goal(session=s_inv, team=inv_y, scorer_id=inv_players[1].id, assist_id=inv_players[2].id),  # Hamsa <- Yusuf
    ])
    db.session.flush()  # Flush to make goals in session

    # --- Optionally finalize one session & simulate MVP votes ---
    # Mark Hidden Leaf as completed now; open voting window (in real app you'd enforce the 3h window)
    s_hidden.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    # Past MVP votes
    # Hidden Leaf past: Khalid, Mubarak, Mohamed, Khadar
    db.session.add_all([
        MvpVote(session=s_hidden_past, voter_id=hidden_players[0].id, voted_for_id=hidden_players[2].id),  # Khalid -> Mubarak
        MvpVote(session=s_hidden_past, voter_id=hidden_players[1].id, voted_for_id=hidden_players[0].id),  # Mohamed -> Khalid
        MvpVote(session=s_hidden_past, voter_id=hidden_players[2].id, voted_for_id=hidden_players[1].id),  # Mubarak -> Mohamed
        MvpVote(session=s_hidden_past, voter_id=hidden_players[3].id, voted_for_id=hidden_players[0].id),  # Khadar -> Khalid
    ])

    # The Boys past: Abdi, Yaya, Ilyas, Ismail
    db.session.add_all([
        MvpVote(session=s_boys_past, voter_id=boys_players[0].id, voted_for_id=boys_players[1].id),  # Abdi -> Yaya
        MvpVote(session=s_boys_past, voter_id=boys_players[1].id, voted_for_id=boys_players[2].id),  # Yaya -> Ilyas
        MvpVote(session=s_boys_past, voter_id=boys_players[2].id, voted_for_id=boys_players[0].id),  # Ilyas -> Abdi
        MvpVote(session=s_boys_past, voter_id=boys_players[3].id, voted_for_id=boys_players[1].id),  # Ismail -> Yaya
    ])

    # Current votes (no self-votes)
    # Participants: Khalid, Mubarak, Mohamed, Khadar
    db.session.add_all([
        MvpVote(session=s_hidden, voter_id=hidden_players[0].id, voted_for_id=hidden_players[1].id),  # Khalid -> Mohamed
        MvpVote(session=s_hidden, voter_id=hidden_players[1].id, voted_for_id=hidden_players[0].id),  # Mohamed -> Khalid
        MvpVote(session=s_hidden, voter_id=hidden_players[2].id, voted_for_id=hidden_players[0].id),  # Mubarak -> Khalid
        MvpVote(session=s_hidden, voter_id=hidden_players[3].id, voted_for_id=hidden_players[1].id),  # Khadar -> Mohamed
    ])
    db.session.flush()  # Flush MVP votes
    db.session.commit()

    print("✅ Seed complete: groups, users, sessions, teams, goals, MVP votes.")
