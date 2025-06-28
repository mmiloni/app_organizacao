import sqlite3
from pathlib import Path

# Define database path
db_path = Path("infos_pendencias.db")

# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_date TEXT,
    content TEXT,
    tag TEXT,
    related_type TEXT,
    related_id INTEGER
);

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    last_interaction TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    conv_date TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES people (id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT CHECK(priority IN ('Alta', 'Média', 'Baixa')) NOT NULL DEFAULT 'Média',
    status TEXT CHECK(status IN ('Pendente', 'Concluído')) NOT NULL DEFAULT 'Pendente',
    created_at TEXT NOT NULL
    deadline TEXT,
);

CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    url TEXT NOT NULL,
    comment TEXT,
    saved_at TEXT NOT NULL
);

""")

# Commit and close
conn.commit()
conn.close()

"Banco de dados inicial 'infos_pendencias.db' criado com sucesso com todas as tabelas principais."
