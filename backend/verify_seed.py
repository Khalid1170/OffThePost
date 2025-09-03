from app import create_app, db
from models import (
    User, Group, GroupMembership,
    Session, SessionTeam, SessionTeamMembership,
    Goal, MvpVote
)

app = create_app()

def verify_seed():
    with app.app_context():
        print("🔍 Verifying seeded data...")

        # Groups
        groups = Group.query.all()
        print(f"📂 Groups: {len(groups)}")
        for g in groups:
            print(f"  - {g.name} (Leader: {g.leader.name if g.leader else 'None'})")

        # Users
        users = User.query.all()
        print(f"👥 Users: {len(users)}")
        for u in users[:5]:  # Show first 5 users with stats
            teams_names = [f"{t.name} ({t.session.group.name})" for t in u.teams_played]
            print(f"  - {u.name}: Fav Team: {u.fav_team}, Position: {u.preferred_position}, Foot: {u.preferred_foot}, Nickname: {u.nickname}")
            print(f"    Stats: Goals: {u.goals_scored_count}, Assists: {u.assists_count}, MVPs: {u.mvp_wins_count}, Teams: {teams_names}")
        if len(users) > 5:
            print(f"  ... and {len(users) - 5} more users")

        # Sessions
        sessions = Session.query.all()
        print(f"⚽ Sessions: {len(sessions)}")
        for s in sessions:
            print(f"  - {s.group.name} at {s.location} on {s.start_time} (Completed: {s.completed_at is not None})")

        # Teams
        teams = SessionTeam.query.all()
        print(f"🏆 Teams: {len(teams)}")
        for t in teams:
            print(f"  - {t.name} in {t.session.group.name} (Captain: {t.captain.name if t.captain else 'None'})")

        # Goals
        goals = Goal.query.all()
        print(f"⚽ Goals: {len(goals)}")
        for g in goals:
            assist_name = g.assistant.name if g.assistant else 'None'
            print(f"  - {g.scorer.name} scored for {g.team.name} in {g.session.group.name} (Assist: {assist_name})")

        # MVP Votes
        votes = MvpVote.query.all()
        print(f"🏆 MVP Votes: {len(votes)}")
        for v in votes:
            print(f"  - {v.voter.name} voted for {v.candidate.name} in {v.session.group.name}")

        # Summary
        print("\n✅ Verification complete!")
        print(f"Total: {len(groups)} groups, {len(users)} users, {len(sessions)} sessions, {len(teams)} teams, {len(goals)} goals, {len(votes)} votes")

if __name__ == "__main__":
    verify_seed()
