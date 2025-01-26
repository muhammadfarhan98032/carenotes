from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from typing import List, Optional
from datetime import datetime

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("db/carenotes.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        residentName TEXT,
                        dateTime TEXT,
                        content TEXT,
                        authorName TEXT
                    )''')
    conn.commit()
    conn.close()

class Note(BaseModel):
    residentName: str
    dateTime: str
    content: str
    authorName: str

@app.post("/notes", response_model=Note)
def create_note(note: Note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (residentName, dateTime, content, authorName) VALUES (?, ?, ?, ?)",
                   (note.residentName, note.dateTime, note.content, note.authorName))
    conn.commit()
    conn.close()
    return note

@app.get("/notes", response_model=List[Note])
def list_notes(residentName: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if residentName:
        cursor.execute("SELECT * FROM notes WHERE residentName = ?", (residentName,))
    else:
        cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return [dict(note) for note in notes]

@app.put("/notes/{id}", response_model=Note)
def update_note(id: int, note: Note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET residentName = ?, dateTime = ?, content = ?, authorName = ? WHERE id = ?",
                   (note.residentName, note.dateTime, note.content, note.authorName, id))
    conn.commit()
    conn.close()
    return note

@app.delete("/notes/{id}")
def delete_note(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    create_table()
