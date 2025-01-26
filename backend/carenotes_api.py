from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
from typing import List, Optional
from datetime import datetime
import os

# Initialize FastAPI app
app = FastAPI()

# Serve static files (Frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

def get_db_connection():
    """Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to interact with the SQLite database.

    Example:
        >>> conn = get_db_connection()
        >>> cursor = conn.cursor()
    """
    conn = sqlite3.connect("db/carenotes.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Creates the database and initializes tables if they do not exist."""

    if not os.path.exists("db"):
        os.makedirs("db")  # Ensure the 'db' directory exists

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure id is AUTO INCREMENT
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        residentName TEXT NOT NULL,
                        dateTime TEXT NOT NULL,
                        content TEXT NOT NULL,
                        authorName TEXT NOT NULL
                    )''')

    # Check if records exist
    cursor.execute("SELECT COUNT(*) FROM notes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO notes (residentName, dateTime, content, authorName) VALUES (?, ?, ?, ?)", [
            ("Alice Johnson", "2024-09-17T10:30:00Z", "Medication administered as scheduled.", "Nurse Smith"),
            ("Bob Williams", "2024-09-17T11:45:00Z", "Assisted with physical therapy exercises.", "Dr. Brown")
        ])
    
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    """Runs on application startup to initialize the database.

    This ensures the database exists and contains at least some initial data.
    
    Example:
        >>> startup_event()
    """
    print("Initializing database...")
    create_database()
    print("Database initialized successfully.")

class Note(BaseModel):
    """Schema for a Care Note object.

    Attributes:
        residentName (str): Name of the resident associated with the note.
        dateTime (str): The timestamp when the note was created.
        content (str): The actual content of the note.
        authorName (str): The name of the author who wrote the note.
    """
    residentName: str
    dateTime: str
    content: str
    authorName: str


@app.post("/notes/create", response_model=Note)
def create_note(note: Note):
    """Creates a new care note in the database and returns the assigned ID.

    Args:
        note (Note): The care note containing residentName, dateTime, content, and authorName.

    Returns:
        dict: The newly created note with its assigned `id`.

    Raises:
        HTTPException: If an internal error occurs while inserting the note.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (residentName, dateTime, content, authorName) VALUES (?, ?, ?, ?)",
            (note.residentName, note.dateTime, note.content, note.authorName),
        )
        new_id = cursor.lastrowid  # ✅ Get the newly assigned ID
        conn.commit()
        conn.close()

        return {
            "id": new_id,  # ✅ Return the new note ID
            "residentName": note.residentName,
            "dateTime": note.dateTime,
            "content": note.content,
            "authorName": note.authorName,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/notes/list")
def list_notes(residentName: Optional[str] = Query(None)):
    """Retrieves a list of care notes, ensuring the ID is correctly included.

    Args:
        residentName (Optional[str], optional): The name of the resident to filter by. Defaults to None.

    Returns:
        List[dict]: A list of notes including their IDs.

    Raises:
        HTTPException: If no notes are found or an internal error occurs.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if residentName:
            cursor.execute("SELECT id, residentName, dateTime, content, authorName FROM notes WHERE residentName = ?", (residentName,))
        else:
            cursor.execute("SELECT id, residentName, dateTime, content, authorName FROM notes")

        notes = cursor.fetchall()
        conn.close()

        if not notes:
            print(" No notes found in database")
            raise HTTPException(status_code=404, detail="No notes found.")

        # Convert rows to dict explicitly
        result = [{"id": note["id"], "residentName": note["residentName"], "dateTime": note["dateTime"], "content": note["content"], "authorName": note["authorName"]} for note in notes]

        print(f" Retrieved {len(result)} notes from database: {result}")
        return result

    except Exception as e:
        print(f" Backend error retrieving notes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.put("/notes/update/{id}", response_model=Note)
def update_note(id: int, note: Note):
    """Updates an existing care note.

    Args:
        id (int): The ID of the note to update.
        note (Note): The updated note data.

    Returns:
        Note: The updated note.

    Raises:
        HTTPException: If the note is not found or an internal error occurs.

    Example:
        >>> update_note(1, Note(residentName="Alice Johnson", dateTime="2024-09-17T10:30:00Z", content="Updated content", authorName="Nurse Smith"))
    """
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
    """Deletes a care note from the database."""

    print(f"🔍 Backend received DELETE request for ID: {id}")  # Debugging output

    if id is None or id <= 0:
        print(" Invalid ID received. Aborting delete.")
        raise HTTPException(status_code=400, detail="Invalid note ID received")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_rows == 0:
            print(f" No note found with ID: {id}")
            raise HTTPException(status_code=404, detail=f"Note with ID {id} not found.")

        print(f"✅ Successfully deleted note with ID: {id}")
        return {"message": f"Note {id} deleted successfully."}

    except Exception as e:
        print(f" Error deleting note: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@app.get("/")
def root():
    """Redirects to the frontend index page.

    Returns:
        RedirectResponse: Redirects the user to `/static/index.html`.
    """
    return RedirectResponse(url="/static/index.html")

@app.get("/favicon.ico")
def favicon():
    """Handles missing favicon requests to prevent errors.

    Raises:
        HTTPException: Always returns a 404 error.
    """
    raise HTTPException(status_code=404, detail="Favicon not found.")
