document.addEventListener("DOMContentLoaded", function () {
    fetchNotes();
});

async function fetchNotes() {
    let residentFilter = document.getElementById('filter').value;
    let url = '/notes/list';
    if (residentFilter) {
        url += `?residentName=${encodeURIComponent(residentFilter)}`;
    }
    
    let response = await fetch(url);
    let data = await response.json();
    let notesContainer = document.getElementById('notes');
    notesContainer.innerHTML = '';

    data.forEach(note => {
        notesContainer.innerHTML += `
            <div class="note">
                <h3>${note.residentName}</h3>
                <p><strong>${new Date(note.dateTime).toLocaleString()}</strong> - ${note.authorName}</p>
                <p>${note.content}</p>
                <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        `;
    });

    populateFilter(data);
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
    await fetch(`/notes/delete/${id}`, { method: 'DELETE' });
    fetchNotes();
}

function populateFilter(notes) {
    let filter = document.getElementById('filter');
    let residents = new Set(notes.map(note => note.residentName));

    filter.innerHTML = '<option value="">All Residents</option>';
    residents.forEach(resident => {
        filter.innerHTML += `<option value="${resident}">${resident}</option>`;
    });
}
