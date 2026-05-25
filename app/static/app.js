// Global Application State
let activeSessionId = null;
let activeProvider = 'gemini';
let quizData = [];
let quizIndex = 0;
let quizScore = 0;
let quizSelectedOption = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchServerConfig();
    setupDragAndDrop();
});

// Fetch active config settings from the FastAPI server
async function fetchServerConfig() {
    try {
        const response = await fetch('/api/config');
        if (response.ok) {
            const data = await response.json();
            activeProvider = data.provider;
            document.getElementById('provider-select').value = activeProvider;
            
            // Check if key is configured for the active provider
            const hasGemini = data.has_gemini_key;
            const hasGroq = data.has_groq_key;
            
            if (activeProvider === 'gemini' && !hasGemini) {
                showToast("Gemini key is missing. Please set GEMINI_API_KEY in .env", "error");
            } else if (activeProvider === 'groq' && !hasGroq) {
                showToast("Groq key is missing. Please set GROQ_API_KEY in .env", "error");
            }
        }
    } catch (error) {
        console.error("Failed to fetch server config:", error);
    }
}

// Update the active AI Provider on the FastAPI backend
async function handleProviderChange() {
    const select = document.getElementById('provider-select');
    const selectedProvider = select.value;
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider: selectedProvider })
        });
        
        if (response.ok) {
            const data = await response.json();
            activeProvider = data.provider;
            showToast(`AI Engine switched to ${activeProvider.toUpperCase()}`, "success");
        } else {
            showToast("Failed to switch AI Engine on backend", "error");
        }
    } catch (error) {
        showToast("Error updating AI Engine configuration", "error");
        console.error(error);
    }
}

// Drag & Drop event bindings
function setupDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            processUpload(files[0]);
        }
    }, false);
}

function triggerFileInput() {
    document.getElementById('file-input').click();
}

function handleFileSelection(event) {
    const files = event.target.files;
    if (files.length > 0) {
        processUpload(files[0]);
    }
}

// Execute PDF upload & vector indexing request
async function processUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast("Unsupported format. Only PDF documents can be processed.", "error");
        return;
    }

    const dropZone = document.getElementById('drop-zone');
    const uploadText = dropZone.querySelector('.upload-text');
    const uploadSub = dropZone.querySelector('.upload-subtext');
    const uploadIcon = dropZone.querySelector('.upload-icon');
    
    // Save original state
    const origText = uploadText.textContent;
    const origSub = uploadSub.textContent;
    
    // Set loading state
    uploadText.textContent = "Uploading & Indexing...";
    uploadSub.textContent = "Generating local vector store...";
    uploadIcon.className = "fa-solid fa-spinner loader-spinner upload-icon";
    dropZone.style.pointerEvents = 'none';

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        
        if (response.ok && data.status === "success") {
            activeSessionId = data.session_id;
            
            // Update UI status widgets
            const badge = document.getElementById('status-badge');
            badge.textContent = "Active";
            badge.className = "info-badge badge-active";
            
            document.getElementById('info-filename').textContent = data.filename;
            document.getElementById('info-filename').title = data.filename;
            document.getElementById('info-chunks').textContent = `${data.chunks_count} segments`;
            document.getElementById('info-size').textContent = `${(file.size / 1024).toFixed(1)} KB`;
            
            // Enable interactive elements
            document.getElementById('chat-textarea').removeAttribute('disabled');
            document.getElementById('chat-textarea').placeholder = "Query your active PDF document here...";
            
            const sendBtn = document.getElementById('btn-send-message');
            sendBtn.removeAttribute('disabled');
            sendBtn.title = "Send message";
            
            const quizBtn = document.getElementById('btn-generate-quiz');
            quizBtn.removeAttribute('disabled');
            quizBtn.title = "Synthesize Quiz";

            showToast("Document indexed and vectorized successfully!", "success");
            
            // Reset upload widget
            uploadText.textContent = "PDF Loaded Successfully";
            uploadSub.textContent = "Click or drag to replace";
            uploadIcon.className = "fa-solid fa-circle-check upload-icon";
            uploadIcon.style.color = "var(--neon-green)";
            
            // Focus chat input
            document.getElementById('chat-textarea').focus();
        } else {
            throw new Error(data.detail || "PDF processing failed.");
        }
    } catch (error) {
        showToast(error.message, "error");
        // Revert upload UI
        uploadText.textContent = origText;
        uploadSub.textContent = origSub;
        uploadIcon.className = "fa-solid fa-file-pdf upload-icon";
        uploadIcon.style.color = "";
    } finally {
        dropZone.style.pointerEvents = 'all';
    }
}

// Switch between Chat and Quiz viewport tabs
function switchTab(tab) {
    const chatTabBtn = document.getElementById('btn-chat-tab');
    const quizTabBtn = document.getElementById('btn-quiz-tab');
    const chatView = document.getElementById('view-chat');
    const quizView = document.getElementById('view-quiz');
    
    if (tab === 'chat') {
        chatTabBtn.classList.add('active');
        quizTabBtn.classList.remove('active');
        chatView.classList.add('active');
        quizView.classList.remove('active');
    } else {
        chatTabBtn.classList.remove('active');
        quizTabBtn.classList.add('active');
        chatView.classList.remove('active');
        quizView.classList.add('active');
    }
}

// Format markdown-like markers into clean HTML strings
function formatMessage(text) {
    if (!text) return "";
    
    // Escape HTML tags to prevent cross-site scripting
    let formatted = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    // Format Bold (**text**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Format list bullets (- bullet or * bullet)
    formatted = formatted.replace(/^\s*[-*]\s+(.*?)$/gm, "<li>$1</li>");
    // Wrap bullet lines in <ul> tags
    formatted = formatted.replace(/(<li>.*?<\/li>)+/g, "<ul>$&</ul>");
    
    // Format linebreaks
    formatted = formatted.replace(/\n/g, "<br>");
    
    return formatted;
}

// Add User/Assistant bubbles to Chat History Panel
function appendChatBubble(sender, text, isLoader = false) {
    const history = document.getElementById('chat-history-container');
    const welcome = document.getElementById('chat-welcome');
    
    if (welcome) {
        welcome.remove();
    }
    
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    if (isLoader) bubble.id = "active-chat-loader";
    
    const avatar = document.createElement('div');
    avatar.className = "bubble-avatar";
    avatar.textContent = sender === 'user' ? 'U' : 'AI';
    
    const body = document.createElement('div');
    body.className = "bubble-body";
    
    if (isLoader) {
        body.innerHTML = `
            <div class="loader-container" style="padding: 0; align-items: flex-start; gap: 0.5rem;">
                <div class="loader-bar" style="width: 100px;"></div>
            </div>
        `;
    } else {
        body.innerHTML = formatMessage(text);
    }
    
    bubble.appendChild(avatar);
    bubble.appendChild(body);
    history.appendChild(bubble);
    
    // Auto-scroll viewport to latest bubble
    history.scrollTop = history.scrollHeight;
}

// Submit chat messages using enter key (and shift-enter for new lines)
function handleChatSubmit(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Call Chat Endpoint
async function sendMessage() {
    const textarea = document.getElementById('chat-textarea');
    const message = textarea.value.trim();
    
    if (!message || !activeSessionId) return;
    
    // Clear text area and disable input briefly to prevent multiple sends
    textarea.value = "";
    textarea.disabled = true;
    
    // Render user bubble
    appendChatBubble('user', message);
    
    // Render AI glowing loading indicator
    appendChatBubble('assistant', "", true);
    
    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                session_id: activeSessionId
            })
        });
        
        const data = await response.json();
        
        // Remove typing loader bubble
        const loader = document.getElementById('active-chat-loader');
        if (loader) loader.remove();
        
        if (response.ok) {
            appendChatBubble('assistant', data.answer);
        } else {
            appendChatBubble('assistant', `⚠️ **Error generating response:** ${data.detail || "Unable to complete request"}`);
            showToast(data.detail || "Chat error occurred", "error");
        }
    } catch (error) {
        const loader = document.getElementById('active-chat-loader');
        if (loader) loader.remove();
        appendChatBubble('assistant', "⚠️ **Network Error:** Could not communicate with server. Check terminal server output.");
        showToast("Connection failed", "error");
        console.error(error);
    } finally {
        textarea.disabled = false;
        textarea.focus();
    }
}

// Quiz View States transitions helper
function toggleQuizView(activeBlockId) {
    const blocks = ['quiz-setup-block', 'quiz-loader', 'quiz-deck-container', 'quiz-results-container'];
    blocks.forEach(id => {
        const el = document.getElementById(id);
        if (id === activeBlockId) {
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    });
}

// API request to synthesize a custom quiz
async function buildQuiz() {
    if (!activeSessionId) return;
    
    const sizeSelect = document.getElementById('quiz-size');
    const numQ = parseInt(sizeSelect.value) || 5;
    
    toggleQuizView('quiz-loader');
    
    try {
        const response = await fetch("/api/quiz", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: activeSessionId,
                num_questions: numQ
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === "success") {
            quizData = data.quiz;
            quizIndex = 0;
            quizScore = 0;
            quizSelectedOption = null;
            
            renderQuizQuestion();
            toggleQuizView('quiz-deck-container');
            showToast(`Quiz generated with ${quizData.length} questions!`, "success");
        } else {
            throw new Error(data.detail || "Failed to generate quiz.");
        }
    } catch (error) {
        showToast(error.message, "error");
        toggleQuizView('quiz-setup-block');
        console.error(error);
    }
}

// Display active question and clear/reset options layout
function renderQuizQuestion() {
    if (!quizData || quizData.length === 0 || quizIndex >= quizData.length) return;
    
    const item = quizData[quizIndex];
    
    // Update Stats & Progress tracker bar
    document.getElementById('quiz-progress-text').textContent = `Question ${quizIndex + 1} of ${quizData.length}`;
    document.getElementById('quiz-score-badge').textContent = `Score: ${quizScore}`;
    
    const progressPercent = ((quizIndex) / quizData.length) * 100;
    document.getElementById('quiz-progress-fill').style.width = `${progressPercent}%`;
    
    // Set Question Title Text
    document.getElementById('quiz-question-text').textContent = item.question;
    
    // Clear and build options list buttons
    const list = document.getElementById('quiz-options-list');
    list.innerHTML = "";
    quizSelectedOption = null;
    
    document.getElementById('btn-next-question').setAttribute('disabled', 'true');
    if (quizIndex === quizData.length - 1) {
        document.getElementById('btn-next-question').innerHTML = 'Finish Quiz <i class="fa-solid fa-circle-check"></i>';
    } else {
        document.getElementById('btn-next-question').innerHTML = 'Next Question <i class="fa-solid fa-arrow-right"></i>';
    }
    
    item.options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = "option-btn";
        btn.textContent = opt;
        btn.onclick = () => selectQuizOption(btn, opt);
        list.appendChild(btn);
    });
}

// Evaluate clickable option selection
function selectQuizOption(clickedBtn, selectedOptionText) {
    if (quizSelectedOption !== null) return; // Prevent clicking multiple times
    
    quizSelectedOption = selectedOptionText;
    const item = quizData[quizIndex];
    const correctAns = item.correct_answer;
    
    const buttons = document.querySelectorAll('#quiz-options-list .option-btn');
    
    // Color code outputs
    buttons.forEach(btn => {
        btn.setAttribute('disabled', 'true'); // Lock options
        
        if (btn.textContent === correctAns) {
            btn.classList.add('correct');
        }
        
        if (btn === clickedBtn && selectedOptionText !== correctAns) {
            btn.classList.add('incorrect');
        }
    });
    
    // Update score
    if (selectedOptionText === correctAns) {
        quizScore++;
        document.getElementById('quiz-score-badge').textContent = `Score: ${quizScore}`;
        showToast("Correct Answer!", "success");
    } else {
        showToast("Incorrect Answer", "error");
    }
    
    // Enable Next button
    document.getElementById('btn-next-question').removeAttribute('disabled');
}

// Advance to subsequent card or compile final performance scores
function advanceQuiz() {
    quizIndex++;
    
    if (quizIndex < quizData.length) {
        renderQuizQuestion();
    } else {
        // Complete state progress fill to 100%
        document.getElementById('quiz-progress-fill').style.width = `100%`;
        showQuizResults();
    }
}

// Render the final performance board card
function showQuizResults() {
    document.getElementById('results-score-num').textContent = quizScore;
    document.getElementById('results-score-total').textContent = `/ ${quizData.length}`;
    
    const pct = (quizScore / quizData.length) * 100;
    const headline = document.getElementById('results-headline');
    const feedback = document.getElementById('results-feedback-text');
    
    if (pct === 100) {
        headline.textContent = "Absolute Masterclass! 🌌";
        feedback.textContent = "Flawless assessment! You scored 100%. You clearly possess total comprehension of the PDF text content.";
    } else if (pct >= 70) {
        headline.textContent = "Exceptional Score! 🚀";
        feedback.textContent = `Wonderful comprehension! You scored ${pct.toFixed(0)}%. Excellent grasp of the fundamental concepts.`;
    } else if (pct >= 40) {
        headline.textContent = "Solid Achievement! ⚡";
        feedback.textContent = `A respectable effort! You scored ${pct.toFixed(0)}%. Review the document material or ask some more questions to solidify the concepts!`;
    } else {
        headline.textContent = "Keep Learning! ☄️";
        feedback.textContent = `You scored ${pct.toFixed(0)}%. PDF documents can contain high-density material. Use the AI Chat assistant to ask questions and try taking the quiz again!`;
    }
    
    toggleQuizView('quiz-results-container');
}

function exitQuiz() {
    toggleQuizView('quiz-setup-block');
}

// Sliding interactive notification toasts
function showToast(message, type = "success") {
    const area = document.getElementById('notification-area');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = document.createElement('i');
    if (type === "success") {
        icon.className = "fa-solid fa-circle-check toast-icon";
    } else {
        icon.className = "fa-solid fa-triangle-exclamation toast-icon";
    }
    
    const text = document.createElement('span');
    text.textContent = message;
    
    toast.appendChild(icon);
    toast.appendChild(text);
    area.appendChild(toast);
    
    // Automatically delete toast from DOM after completion of animations
    setTimeout(() => {
        toast.style.animation = "slideInToast 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse";
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}
