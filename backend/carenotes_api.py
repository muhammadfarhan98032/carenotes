from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI()

# Serve static files (Frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

def get_db_connection():
    conn = sqlite3.connect("db/carenotes.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Creates the database and seeds initial data if empty."""
    if not os.path.exists("db"):
        os.makedirs("db")  # Ensure the db directory exists

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create notes table if it does not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        residentName TEXT,
                        dateTime TEXT,
                        content TEXT,
                        authorName TEXT
                    )''')

    # Seed data if table is empty
    cursor.execute("SELECT COUNT(*) FROM notes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO notes (residentName, dateTime, content, authorName) VALUES (?, ?, ?, ?)", [
            ("Alice Johnson", "2024-09-17T10:30:00Z", "Medication administered as scheduled.", "Nurse Smith"),
            ("Bob Williams", "2024-09-17T11:45:00Z", "Assisted with physical therapy exercises.", "Dr. Brown")
        ])
    
    conn.commit()
    conn.close()

# ✅ Ensure database is created before app starts
@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    create_database()
    print("Database initialized successfully.")

class Note(BaseModel):
    residentName: str
    dateTime: str
    content: str
    authorName: str

@app.post("/notes/create", response_model=Note)
def create_note(note: Note):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (residentName, dateTime, content, authorName) VALUES (?, ?, ?, ?)",
                    (note.residentName, note.dateTime, note.content, note.authorName))
        conn.commit()
        conn.close()
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/notes/list", response_model=List[Note])
def list_notes(residentName: Optional[str] = Query(None)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if residentName:
            cursor.execute("SELECT * FROM notes WHERE residentName = ?", (residentName,))
        else:
            cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        conn.close()
        if not notes:
            raise HTTPException(status_code=404, detail="No notes found.")
        return [dict(note) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.put("/notes/update/{id}", response_model=Note)
def update_note(id: int, note: Note):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET residentName = ?, dateTime = ?, content = ?, authorName = ? WHERE id = ?",
                    (note.residentName, note.dateTime, note.content, note.authorName, id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found.")
        conn.commit()
        conn.close()
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.delete("/notes/delete/{id}")
def delete_note(id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found.")
        conn.commit()
        conn.close()
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/")
def root():
    """Redirects to the index page."""
    return RedirectResponse(url="/static/index.html")

@app.get("/favicon.ico")
def favicon():
    raise HTTPException(status_code=404, detail="Favicon not found.")
