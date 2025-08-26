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





