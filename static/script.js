const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const processBtn = document.getElementById('process-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const resultsSection = document.getElementById('results-section');
const tableBody = document.getElementById('table-body');
let selectedFile = null;

// Drag & Drop Events
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
    if (file.name.endsWith('.csv')) {
        selectedFile = file;
        dropZone.querySelector('p').innerHTML = `Selected: <strong>${file.name}</strong>`;
        processBtn.disabled = false;
    } else {
        alert("Please upload a valid CSV file.");
    }
}

// Process API Call
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    loadingOverlay.classList.remove('hidden');

    try {
        const response = await fetch('/api/triage', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        renderTable(data.results);
        
        loadingOverlay.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Scroll to results smoothly
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        console.error(err);
        alert("An error occurred while processing the CSV.");
        loadingOverlay.classList.add('hidden');
    }
});

function renderTable(results) {
    tableBody.innerHTML = "";
    
    results.forEach((row, i) => {
        const tr = document.createElement('tr');
        
        // Staggered fade in animation
        tr.style.opacity = '0';
        tr.style.transform = 'translateY(10px)';
        tr.style.transition = `all 0.3s ease ${i * 0.05}s`;
        
        const badgeClass = row.decision === 'ESCALATE' ? 'escalate' : 'reply';
        
        // Truncate response
        const snippet = row.response.length > 80 ? row.response.substring(0, 80) + '...' : row.response;

        tr.innerHTML = `
            <td>${row.ticket_id}</td>
            <td>${row.product_area}</td>
            <td><span class="badge ${badgeClass}">${row.decision}</span></td>
            <td><small style="color: var(--text-muted)">${snippet}</small></td>
        `;
        
        tableBody.appendChild(tr);
        
        // Trigger reflow for animation
        setTimeout(() => {
            tr.style.opacity = '1';
            tr.style.transform = 'translateY(0)';
        }, 10);
    });
}
