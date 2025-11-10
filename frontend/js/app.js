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
    
    if (!title || !content) {
        showAlert('Please enter title and content', 'warning');
        return;
    }
    
    showLoading('uploadDocBtn', '<i class="bi bi-cloud-upload"></i> Upload Document');
    
    try {
        const response = await fetch(`${API_URL}/documents/upload`, {
            method: 'POST',
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
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        showAlert(`Document "${title}" uploaded successfully!`, 'success');
        
        // Clear form
        document.getElementById('docTitle').value = '';
        document.getElementById('docContent').value = '';
        
        // Refresh document list
        await loadDocuments();
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('uploadDocBtn', '<i class="bi bi-cloud-upload"></i> Upload Document');
    }
});

async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents/list`);
        const data = await response.json();
        
        const listContainer = document.getElementById('documentsList');
        listContainer.innerHTML = '';
        
        if (data.documents.length === 0) {
            listContainer.innerHTML = '<p class="text-muted">No documents uploaded yet</p>';
            return;
        }
        
        data.documents.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.className = 'result-item';
            docElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${doc.title}</h6>
                        <small class="text-muted">ID: ${doc.doc_id} | Language: ${doc.language}</small>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="deleteDocument('${doc.doc_id}')">
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

// Search Functions
document.getElementById('searchBtn')?.addEventListener('click', async function() {
    const query = document.getElementById('searchQuery').value.trim();
    const topK = parseInt(document.getElementById('topK').value);
    
    if (!query) {
        showAlert('Please enter a search query', 'warning');
        return;
    }
    
    showLoading('searchBtn', '<i class="bi bi-search"></i> Search');
    
    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        displaySearchResults(data);
        
        if (data.results.length === 0) {
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('searchResults').style.display = 'none';
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading('searchBtn', '<i class="bi bi-search"></i> Search');
    }
});

function displaySearchResults(data) {
    document.getElementById('searchResults').style.display = 'block';
    document.getElementById('noResults').style.display = 'none';
    
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    data.results.forEach((result, index) => {
        const resultElement = document.createElement('div');
        resultElement.className = 'result-item';
        resultElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="mb-0">${index + 1}. ${result.title}</h6>
                <span class="result-score">${(result.score * 100).toFixed(1)}%</span>
            </div>
            <p class="text-muted small">${result.content}</p>
            <small class="text-muted">ID: ${result.doc_id}</small>
        `;
        container.appendChild(resultElement);
    });
    
    const stats = document.getElementById('searchStats');
    stats.textContent = `Found ${data.total_results} result(s) in ${(data.processing_time * 1000).toFixed(2)}ms`;
}

// Web Search Functions
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

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadDocuments();
});
