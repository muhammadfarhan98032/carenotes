# Care Notes Application

A FastAPI-based application for managing care notes. It allows users to add, view, update, delete, and filter notes for residents. The frontend is built using HTML, CSS, and JavaScript, while the backend uses SQLite3 as a lightweight database.

## Features
- Add Care Notes with Resident Name, Author Name, and Content
- View & Filter Notes by Resident Name
- Edit Existing Notes
- Delete Notes
- Persistent Storage using SQLite3
- FastAPI Backend with RESTful API Endpoints
- Minimal UI with HTML, CSS, and JavaScript

## Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/muhammadfarhan98032/carenotes.git
cd carenotes
```

### 2. Set Up a Virtual Environment (Optional, Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Application
```sh
python -m uvicorn backend.carenotes_api:app --reload
```
- The backend will start at `http://127.0.0.1:8000`
- Open `http://127.0.0.1:8000/static/index.html` in your browser.

## Project Structure
```
carenotes/
│── backend/
│   ├── carenotes_api.py        # FastAPI Backend
├── db/                     # SQLite3 Database Folder
│── frontend/
│   ├── index.html              # Main UI Page
│   ├── script.js               # Frontend Logic
│   ├── style.css               # Styling
│── requirements.txt            # Python Dependencies
│── README.md                   # Documentation
```

## API Endpoints

### 1. Create a Note
- **Endpoint:** `POST /notes/create`
- **Request Body:**
  ```json
  {
    "residentName": "Alice Johnson",
    "dateTime": "2024-09-17T10:30:00Z",
    "content": "Medication administered as scheduled.",
    "authorName": "Nurse Smith"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "residentName": "Alice Johnson",
    "dateTime": "2024-09-17T10:30:00Z",
    "content": "Medication administered as scheduled.",
    "authorName": "Nurse Smith"
  }
  ```

### 2. Retrieve All Notes
- **Endpoint:** `GET /notes/list`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "residentName": "Alice Johnson",
      "dateTime": "2024-09-17T10:30:00Z",
      "content": "Medication administered as scheduled.",
      "authorName": "Nurse Smith"
    },
    {
      "id": 2,
      "residentName": "Bob Williams",
      "dateTime": "2024-09-17T11:45:00Z",
      "content": "Assisted with physical therapy exercises.",
      "authorName": "Dr. Brown"
    }
  ]
  ```

### 3. Update a Note
- **Endpoint:** `PUT /notes/update/{id}`
- **Request Body:**
  ```json
  {
    "residentName": "Alice Johnson",
    "dateTime": "2024-09-18T08:00:00Z",
    "content": "Updated content for the note.",
    "authorName": "Nurse Smith"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "residentName": "Alice Johnson",
    "dateTime": "2024-09-18T08:00:00Z",
    "content": "Updated content for the note.",
    "authorName": "Nurse Smith"
  }
  ```

### 4. Delete a Note
- **Endpoint:** `DELETE /notes/delete/{id}`
- **Response:**
  ```json
  {
    "message": "Note deleted successfully"
  }
  ```

## Troubleshooting

### Database Issues
If you face database errors, try deleting the database and restarting:
```sh
rm -rf db/carenotes.db
python -m uvicorn backend.carenotes_api:app --reload
```

### Frontend Not Displaying Notes?
1. Open Developer Console (`F12` > Console).
2. Run:
   ```js
   fetch('/notes/list').then(res => res.json()).then(data => console.log(data))
   ```
3. Ensure notes are returned in the browser console.

## requirements.txt
```
fastapi
uvicorn
pydantic
sqlite3 (sqlite3 is preinstalled if you are going to use someother DB you can use it)
```

## Contributors
- Muhammad Farhan - Lead Developer



## Future Enhancements
- Add User Authentication
- Implement Pagination
- Improve UI Design



