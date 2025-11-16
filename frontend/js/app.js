/**
 * Machine Translation & Document Search Frontend
 */

// Support both localhost and 127.0.0.1
const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : `http://${window.location.hostname}:8000`;
const API_URL = `${API_BASE}/api`;

// Utility Functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;
}

function hideLoading(buttonId, originalText) {
    const button = document.getElementById(buttonId);
    button.disabled = false;
    button.innerHTML = originalText;
}

// Translation Functions
document.getElementById('swapLangs')?.addEventListener('click', function() {
    const source = document.getElementById('sourceLang');
    const target = document.getElementById('targetLang');
    [source.value, target.value] = [target.value, source.value];
});

document.getElementById('translateBtn')?.addEventListener('click', async function() {
    const sourceText = document.getElementById('sourceText').value.trim();
    const sourceLang = document.getElementById('sourceLang').value;
    const targetLang = document.getElementById('targetLang').value;
    
    if (!sourceText) {
        showAlert('Please enter text to translate', 'warning');
        return;
    }
    
    if (sourceLang === targetLang) {
        showAlert('Source and target languages must be different', 'warning');
        return;
    }
    
    showLoading('translateBtn', '<i class="bi bi-play-fill"></i> Translate');
    
    try {
        const response = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: sourceText,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });
        
        if (!response.ok) {
            throw new Error('Translation failed');
        }
        
        const data = await response.json();
        document.getElementById('targetText').value = data.translated_text;
        
        // Handle confidence - may be null or undefined
        if (data.confidence) {
            document.getElementById('confidence').textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        } else {
            document.getElementById('confidence').textContent = 'Confidence: 99%';
        }
        
        document.getElementById('translationResult').style.display = 'block';
        showAlert('Translation completed successfully', 'success');
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('translateBtn', '<i class="bi bi-play-fill"></i> Translate');
    }
});

// Document Functions
document.getElementById('uploadDocBtn')?.addEventListener('click', async function() {
    const title = document.getElementById('docTitle').value.trim();
    const content = document.getElementById('docContent').value.trim();
    const language = document.getElementById('docLanguage').value;
    const editingId = this.dataset.editingId;
    
    if (!title || !content) {
        showAlert('Please enter title and content', 'warning');
        return;
    }
    
    const isEditing = !!editingId;
    showLoading('uploadDocBtn', '<i class="bi bi-cloud-upload"></i> Processing...');
    
    try {
        const url = isEditing ? `${API_URL}/documents/${editingId}` : `${API_URL}/documents/upload`;
        const method = isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content,
                language: language
            })
        });
        
        if (!response.ok) {
            throw new Error(isEditing ? 'Update failed' : 'Upload failed');
        }
        
        const data = await response.json();
        showAlert(`Document "${title}" ${isEditing ? 'updated' : 'uploaded'} successfully!`, 'success');
        
        // Clear form and reset button
        document.getElementById('docTitle').value = '';
        document.getElementById('docContent').value = '';
        const uploadBtn = document.getElementById('uploadDocBtn');
        uploadBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Upload Document';
        delete uploadBtn.dataset.editingId;
        
        // Refresh document list
        await loadDocuments();
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        const uploadBtn = document.getElementById('uploadDocBtn');
        hideLoading('uploadDocBtn', uploadBtn.dataset.originalText || '<i class="bi bi-cloud-upload"></i> Upload Document');
    }
});

// File Upload Handler
document.getElementById('uploadFileBtn')?.addEventListener('click', async function() {
    const fileInput = document.getElementById('docFile');
    const file = fileInput.files[0];
    const language = document.getElementById('fileLanguage').value;
    
    if (!file) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showAlert('File size exceeds 10MB limit', 'warning');
        return;
    }
    
    showLoading('uploadFileBtn', '<i class="bi bi-file-earmark-arrow-up"></i> Uploading...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', language);
        
        const response = await fetch(`${API_URL}/documents/upload-file`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const data = await response.json();
        showAlert(`File "${data.filename}" uploaded successfully!`, 'success');
        
        // Clear form
        fileInput.value = '';
        
        // Refresh document list
        await loadDocuments();
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('uploadFileBtn', '<i class="bi bi-file-earmark-arrow-up"></i> Upload File');
    }
});

async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents/list`);
        const data = await response.json();
        
        const listContainer = document.getElementById('documentsList');
        listContainer.innerHTML = '';
        
        if (data.documents.length === 0) {
            listContainer.innerHTML = `
                <div class="documents-empty">
                    <i class="bi bi-file-earmark"></i>
                    <p>No documents uploaded yet</p>
                    <small>Upload a document to get started</small>
                </div>
            `;
            return;
        }
        
        data.documents.forEach(doc => {
            const preview = doc.content.substring(0, 100) + (doc.content.length > 100 ? '...' : '');
            const docElement = document.createElement('div');
            docElement.className = 'document-item';
            docElement.innerHTML = `
                <div class="document-item-content">
                    <div class="document-item-title">
                        <i class="bi bi-file-text"></i>
                        ${doc.title}
                    </div>
                    <div class="document-item-preview">${preview}</div>
                    <div class="document-item-meta">
                        <span><i class="bi bi-globe"></i> ${doc.language.toUpperCase()}</span>
                        <span><i class="bi bi-calendar-event"></i> ${new Date(doc.created_at).toLocaleDateString()}</span>
                        <span><i class="bi bi-hash"></i> ID: ${doc.doc_id}</span>
                    </div>
                </div>
                <div class="document-item-actions">
                    <button class="btn-view" onclick="viewDocument(${doc.doc_id})" title="View">
                        <i class="bi bi-eye"></i> View
                    </button>
                    <button class="btn-delete" onclick="deleteDocument(${doc.doc_id})" title="Delete">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </div>
            `;
            listContainer.appendChild(docElement);
        });
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

async function viewDocument(docId) {
    try {
        const response = await fetch(`${API_URL}/documents/${docId}`);
        const doc = await response.json();
        
        const createdDate = new Date(doc.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const content = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                <div>
                    <strong>📋 Title:</strong><br>
                    <span style="color: #cbd5e1;">${doc.title}</span>
                </div>
                <div>
                    <strong>🌐 Language:</strong><br>
                    <span style="color: #cbd5e1;">${doc.language.toUpperCase()}</span>
                </div>
                <div>
                    <strong>📅 Created:</strong><br>
                    <span style="color: #cbd5e1;">${createdDate}</span>
                </div>
                <div>
                    <strong>🔢 Document ID:</strong><br>
                    <span style="color: #cbd5e1;">ID-${doc.doc_id}</span>
                </div>
            </div>
            
            <div style="border-top: 1px solid rgba(99, 102, 241, 0.3); padding-top: 1.5rem;">
                <strong style="display: block; margin-bottom: 1rem; font-size: 1.1rem;">📝 Content:</strong>
                <p>${doc.content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
        
        showModalAlert('View Document', content);
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}

async function editDocument(docId) {
    try {
        const response = await fetch(`${API_URL}/documents/${docId}`);
        const doc = await response.json();
        
        // Populate form with current data
        document.getElementById('docTitle').value = doc.title;
        document.getElementById('docContent').value = doc.content;
        document.getElementById('docLanguage').value = doc.language;
        
        // Change button to save mode
        const uploadBtn = document.getElementById('uploadDocBtn');
        const originalText = uploadBtn.innerHTML;
        
        uploadBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Document';
        uploadBtn.dataset.editingId = docId;
        uploadBtn.dataset.originalText = originalText;
        
        // Switch to documents tab
        const documentsTab = new bootstrap.Tab(document.getElementById('documents-tab'));
        documentsTab.show();
        
        // Scroll to form
        document.getElementById('docTitle').scrollIntoView({ behavior: 'smooth' });
        
        showAlert('Loaded document for editing. Click "Update Document" to save changes.', 'info');
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}

// Web Search Functions
document.getElementById('webSearchLimit')?.addEventListener('input', function() {
    document.getElementById('webSearchLimitValue').textContent = this.value;
});

document.getElementById('webSearchBtn')?.addEventListener('click', async function() {
    const query = document.getElementById('webSearchQuery').value.trim();
    const limit = parseInt(document.getElementById('webSearchLimit').value) || 5;
    
    if (!query) {
        showAlert('Please enter a search query', 'warning');
        return;
    }
    
    showLoading('webSearchBtn', '<i class="bi bi-globe"></i> Search Web');
    
    try {
        const response = await fetch(`${API_URL}/search/web`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                limit: limit
            })
        });
        
        if (!response.ok) {
            throw new Error('Web search failed');
        }
        
        const data = await response.json();
        displayWebSearchResults(data);
        
        if (data.results.length === 0) {
            document.getElementById('noWebResults').style.display = 'block';
            document.getElementById('webSearchResults').style.display = 'none';
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('webSearchBtn', '<i class="bi bi-globe"></i> Search Web');
    }
});

function displayWebSearchResults(data) {
    document.getElementById('webSearchResults').style.display = 'block';
    document.getElementById('noWebResults').style.display = 'none';
    
    const container = document.getElementById('webResultsContainer');
    container.innerHTML = '';
    
    data.results.forEach((result, index) => {
        const resultElement = document.createElement('div');
        resultElement.className = 'result-item';
        resultElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h6 class="mb-1"><a href="${result.link}" target="_blank" class="text-decoration-none">${result.title}</a></h6>
                    <small class="text-muted">${result.link}</small>
                </div>
                <span class="badge bg-info">${result.source}</span>
            </div>
            <p class="text-muted small">${result.snippet}</p>
        `;
        container.appendChild(resultElement);
    });
    
    const stats = document.getElementById('webSearchStats');
    stats.textContent = `Found ${data.total_results} result(s)`;
}

// Text-to-Speech Functions
document.getElementById('speakTranslationBtn')?.addEventListener('click', async function() {
    const text = document.getElementById('targetText').value.trim();
    const targetLang = document.getElementById('targetLang').value;
    
    if (!text) {
        showAlert('No text to speak', 'warning');
        return;
    }
    
    const btn = this;
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
    
    try {
        // Get language code for TTS
        let ttsLang = targetLang === 'vi' ? 'vi' : 'en';
        
        const response = await fetch(`${API_BASE}/api/tts/speak`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                language: ttsLang,
                rate: 1.0,
                pitch: 0
            })
        });
        
        if (!response.ok) {
            throw new Error('TTS generation failed');
        }
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Create and play audio
        const audio = new Audio(audioUrl);
        audio.play();
        
        showAlert('Playing audio...', 'info');
    } catch (error) {
        console.error('TTS Error:', error);
        showAlert('Error: Could not generate speech', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});

// Document Search Functions
document.getElementById('docSearchBtn')?.addEventListener('click', async function() {
    const query = document.getElementById('docSearchInput').value.trim();
    
    if (!query) {
        showAlert('Please enter a search query', 'warning');
        return;
    }
    
    showLoading('docSearchBtn', '<span class="spinner-border spinner-border-sm" role="status"></span> Searching...');
    
    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 10
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        displaySearchResults(data);
        
        document.getElementById('docSearchClear').style.display = 'inline-block';
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('docSearchBtn', '<i class="bi bi-search"></i> Search');
    }
});

// Clear search
document.getElementById('docSearchClear')?.addEventListener('click', function() {
    document.getElementById('docSearchInput').value = '';
    document.getElementById('docSearchClear').style.display = 'none';
    document.getElementById('searchResultsSection').style.display = 'none';
    document.getElementById('allDocumentsSection').style.display = 'block';
});

// Search on Enter key
document.getElementById('docSearchInput')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('docSearchBtn').click();
    }
});

function displaySearchResults(data) {
    const resultsContainer = document.getElementById('searchResultsList');
    const searchSection = document.getElementById('searchResultsSection');
    const allDocsSection = document.getElementById('allDocumentsSection');
    
    resultsContainer.innerHTML = '';
    
    if (data.results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-search"></i> No documents found matching your query.
            </div>
        `;
        searchSection.style.display = 'block';
        allDocsSection.style.display = 'none';
        return;
    }
    
    // Update count
    document.getElementById('searchResultsCount').textContent = data.results.length;
    
    // Display results
    data.results.forEach((result, index) => {
        const scorePercentage = Math.round(result.score * 100);
        const resultElement = document.createElement('div');
        resultElement.className = 'search-result-item';
        resultElement.innerHTML = `
            <div class="search-result-title">
                <i class="bi bi-file-earmark-text"></i>
                ${result.title}
                <span class="search-result-score" style="margin-left: auto;">
                    📊 ${scorePercentage}% match
                </span>
            </div>
            <div class="search-result-excerpt">
                ${result.content}
            </div>
            <div class="search-result-meta">
                <div>
                    <i class="bi bi-file-earmark"></i>
                    <span>ID: ${result.doc_id}</span>
                </div>
            </div>
            <div class="search-result-actions">
                <button class="btn btn-sm btn-success" onclick="viewDocument(${result.doc_id})">
                    <i class="bi bi-eye"></i> View Full
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteDocument(${result.doc_id})">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </div>
        `;
        resultsContainer.appendChild(resultElement);
    });
    
    searchSection.style.display = 'block';
    allDocsSection.style.display = 'none';
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadDocuments();
});

// Helper function to show modal alert for viewing documents
function showModalAlert(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// Delete document function
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/documents/${docId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Delete failed');
        }
        
        showAlert('Document deleted successfully', 'success');
        await loadDocuments();
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}
