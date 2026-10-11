from models import db, TrainingSession

def blocking_sessions(date, coach_id, exclude_id=None):
    q = db.select(TrainingSession).where(TrainingSession.coach_id == coach_id,
                                                            TrainingSession.date == date,
                                                            TrainingSession.session_status != "cancelled")
    if exclude_id is not None:
        q = q.where(TrainingSession.id != exclude_id)
    return db.session.execute(q).scalars().all()