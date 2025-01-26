document.addEventListener("DOMContentLoaded", function () {
    fetchNotes();
});

async function fetchNotes() {
    console.log(" Fetching notes...");

    let residentFilter = document.getElementById('filter').value;
    let url = '/notes/list';
    if (residentFilter) {
        url += `?residentName=${encodeURIComponent(residentFilter)}`;
    }

    try {
        let response = await fetch(url);

        if (!response.ok) {
            console.error(" API Error:", response.status);
            alert("Failed to fetch notes. Server error.");
            return;
        }

        let data = await response.json();
        console.log(" Notes received from API:", data);

        let notesContainer = document.getElementById('notes');
        notesContainer.innerHTML = '';

        if (data.length === 0) {
            console.warn(" No notes available to display.");
            notesContainer.innerHTML = "<p>No notes found.</p>";
            return;
        }

        data.forEach(note => {
            if (!note.id || isNaN(note.id)) {
                console.error(" Missing or invalid ID for note:", note);
                return;
            }

            console.log(` Rendering note with ID: ${note.id}`);

            notesContainer.innerHTML += `
                <div class="note" data-id="${note.id}">
                    <h3>${note.residentName}</h3>
                    <p><strong>${new Date(note.dateTime).toLocaleString()}</strong> - ${note.authorName}</p>
                    <p>${note.content}</p>
                    <button class="edit-btn" onclick="editNote(${note.id})">Edit</button>
                    <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
                </div>
            `;
        });

        populateFilter(data);
    } catch (error) {
        console.error(" Request error:", error);
        alert("Error fetching notes. Check console for details.");
    }
}





async function addNote() {
    let residentName = document.getElementById('residentName').value;
    let authorName = document.getElementById('authorName').value;
    let content = document.getElementById('content').value;
    let dateTime = new Date().toISOString();
    
    await fetch('/notes/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ residentName, authorName, content, dateTime })
    });

    fetchNotes();
}

async function deleteNote(id) {
    console.log(" Attempting to delete note. Received ID:", id);  // Debugging log

    if (!id || isNaN(id) || id === "undefined" || id === "null") {
        console.error(" Invalid note ID received:", id);
        alert("Invalid note ID. Please try again.");
        return;
    }

    try {
        let response = await fetch(`/notes/delete/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            let errorData = await response.json();
            console.error(" Error deleting note:", errorData.detail);
            alert("Failed to delete note: " + errorData.detail);
        } else {
            console.log(` Successfully deleted note with ID: ${id}`);
            fetchNotes();  // Refresh the notes list after deletion
        }
    } catch (error) {
        console.error(" Request error:", error);
    }
}

function editNote(id) {
    console.log(`🛠️ Editing note ID: ${id}`);

    // Find the note in the existing notes
    let noteElement = document.querySelector(`div.note[data-id="${id}"]`);
    if (!noteElement) {
        console.error(" Note element not found.");
        return;
    }

    // Extract note details
    let residentName = noteElement.querySelector("h3").innerText;
    let authorName = noteElement.querySelector("p strong").innerText.split(" - ")[1]; 
    let content = noteElement.querySelectorAll("p")[1].innerText;

    // Populate the form
    document.getElementById("editNoteId").value = id;
    document.getElementById("editResidentName").value = residentName;
    document.getElementById("editAuthorName").value = authorName;
    document.getElementById("editContent").value = content;

    // Show the edit form
    document.getElementById("editFormContainer").style.display = "block";
}
async function updateNote() {
    let id = document.getElementById("editNoteId").value;
    let residentName = document.getElementById("editResidentName").value;
    let authorName = document.getElementById("editAuthorName").value;
    let content = document.getElementById("editContent").value;
    let dateTime = new Date().toISOString(); // Update with current timestamp

    console.log(` Updating note ID: ${id}`);

    let response = await fetch(`/notes/update/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ residentName, dateTime, content, authorName })
    });

    if (!response.ok) {
        let errorData = await response.json();
        console.error(" Error updating note:", errorData.detail);
        alert("Failed to update note: " + errorData.detail);
        return;
    }

    console.log(` Successfully updated note ID: ${id}`);
    document.getElementById("editFormContainer").style.display = "none"; // Hide form
    fetchNotes();  // Refresh the list
}
function cancelEdit() {
    console.log(" Edit cancelled.");
    document.getElementById("editFormContainer").style.display = "none";
}





function populateFilter(notes) {
    let filter = document.getElementById('filter');
    let residents = new Set(notes.map(note => note.residentName));

    filter.innerHTML = '<option value="">All Residents</option>';
    residents.forEach(resident => {
        filter.innerHTML += `<option value="${resident}">${resident}</option>`;
    });
}
