"""
Database operations using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from modules.config import DB_FILE

Base = declarative_base()
engine = create_engine(DB_FILE, echo=False)
Session = sessionmaker(bind=engine)

class Score(Base):
    __tablename__ = 'scores'
    __table_args__ = (
        CheckConstraint("mode in ('Easy','Medium','Hard')", name='check_mode'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    duration_sec = Column(Float, nullable=False)
    played_at = Column(String, nullable=False)

def db_init():
    """Initialize the database"""
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        print(f"Error initializing database: {e}")

def db_add_score(player: str, mode: str, score: int, duration_sec: float, played_at: str = None):
    """Add a new score to the database"""
    from datetime import datetime
    if not played_at:
        played_at = datetime.now().isoformat(timespec='seconds')
    
    try:
        session = Session()
        new_score = Score(
            player=player,
            mode=mode,
            score=score,
            duration_sec=float(duration_sec),
            played_at=played_at
        )
        session.add(new_score)
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error adding score: {e}")
        session.rollback()
    finally:
        session.close()

def db_get_scores(mode_filter: str = None):
    """Get scores from the database, optionally filtered by mode"""
    try:
        session = Session()
        query = session.query(Score)
        
        if mode_filter and mode_filter in ("Easy", "Medium", "Hard"):
            query = query.filter(Score.mode == mode_filter)
            
        results = query.order_by(Score.score.desc(), Score.played_at.desc()).all()
        
        return [(r.id, r.player, r.mode, r.score, r.duration_sec, r.played_at) for r in results]
    except SQLAlchemyError as e:
        print(f"Error getting scores: {e}")
        return []
    finally:
        session.close()

def db_update_score(record_id: int, player: str = None, mode: str = None, score: int = None):
    """Update an existing score in the database"""
    try:
        session = Session()
        score_obj = session.query(Score).filter(Score.id == record_id).first()
        
        if not score_obj:
            print(f"Score with id {record_id} not found")
            return
            
        if player is not None:
            score_obj.player = player
        if mode is not None:
            score_obj.mode = mode
        if score is not None:
            score_obj.score = int(score)
            
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error updating score: {e}")
        session.rollback()
    finally:
        session.close()

def db_delete_score(record_id: int):
    """Delete a score from the database"""
    try:
        session = Session()
        score_obj = session.query(Score).filter(Score.id == record_id).first()
        
        if score_obj:
            session.delete(score_obj)
            session.commit()
    except SQLAlchemyError as e:
        print(f"Error deleting score: {e}")
        session.rollback()
    finally:
        session.close()
