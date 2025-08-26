import sqlite3

DATABASE = 'db/game.db'

def init_db():
    db_connection = sqlite3.connect(DATABASE)
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY,
            player TEXT NOT NULL,
            score INTEGER NOT NULL,
            created at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """)
    db_connection.commit()
    db_connection.close()


def save_score(player, score):
    db_connection = sqlite3.connect(DATABASE)
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        INSERT INTO scores(player, score) VALUES (?, ?)
    """,(player, int(score))
    )
    db_connection.commit()
    db_connection.close()


def get_highest_score(limit = 10):
    db_connection = sqlite3.connect(DATABASE)
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        """
            SELECT player, score, created_at FROM scores ORDER BY score DESC, created_at ASC LIMIT ?
        """, (limit)
    )
    rows = db_cursor.fetchall()
    db_connection.commit()
    db_connection.close()

    return rows
