document.addEventListener('DOMContentLoaded', () => {
    const pdfUpload = document.getElementById('pdf-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadStatus = document.getElementById('upload-status');
    
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');
    
    const numQuestions = document.getElementById('num-questions');
    const generateQuizBtn = document.getElementById('generate-quiz-btn');
    const quizBox = document.getElementById('quiz-box');

    let isPdfUploaded = false;

    // File selection
    pdfUpload.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            uploadBtn.disabled = false;
        } else {
            fileNameDisplay.textContent = 'No file chosen';
            uploadBtn.disabled = true;
        }
    });

    // Upload PDF
    uploadBtn.addEventListener('click', async () => {
        const file = pdfUpload.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<div class="loader"></div>';
        uploadStatus.textContent = '';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                uploadStatus.style.color = '#4ade80';
                uploadStatus.textContent = 'Upload successful! You can now chat and generate quizzes.';
                isPdfUploaded = true;
                
                // Enable chat and quiz
                chatInput.disabled = false;
                sendBtn.disabled = false;
                generateQuizBtn.disabled = false;
                
                addMessageToChat('system', 'PDF loaded successfully. What would you like to know?');
            } else {
                uploadStatus.style.color = '#f87171';
                uploadStatus.textContent = result.detail || 'Upload failed.';
                uploadBtn.disabled = false;
            }
        } catch (error) {
            uploadStatus.style.color = '#f87171';
            uploadStatus.textContent = 'An error occurred during upload.';
            uploadBtn.disabled = false;
        } finally {
            uploadBtn.innerHTML = 'Upload';
        }
    });

    // Chat functionality
    const sendMessage = async () => {
        const question = chatInput.value.trim();
        if (!question || !isPdfUploaded) return;

        addMessageToChat('user', question);
        chatInput.value = '';
        sendBtn.disabled = true;
        
        const loaderId = addMessageToChat('bot', '<div class="loader"></div>');

        const formData = new FormData();
        formData.append('question', question);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            const loaderElement = document.getElementById(loaderId);
            if (response.ok) {
                loaderElement.innerHTML = parseMarkdown(result.answer);
            } else {
                loaderElement.innerHTML = `<span style="color:#f87171">Error: ${result.detail}</span>`;
            }
        } catch (error) {
            const loaderElement = document.getElementById(loaderId);
            loaderElement.innerHTML = '<span style="color:#f87171">Failed to connect to server.</span>';
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Quiz functionality
    generateQuizBtn.addEventListener('click', async () => {
        if (!isPdfUploaded) return;

        const count = numQuestions.value;
        generateQuizBtn.disabled = true;
        generateQuizBtn.innerHTML = '<div class="loader"></div>';
        
        quizBox.innerHTML = '';
        addMessageToQuiz('system', 'Generating quiz, please wait...');

        const formData = new FormData();
        formData.append('num_questions', count);

        try {
            const response = await fetch('/quiz', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            quizBox.innerHTML = ''; // Clear system message
            if (response.ok) {
                addMessageToQuiz('bot', parseMarkdown(result.quiz));
            } else {
                addMessageToQuiz('bot', `<span style="color:#f87171">Error: ${result.detail}</span>`);
            }
        } catch (error) {
            quizBox.innerHTML = '';
            addMessageToQuiz('bot', '<span style="color:#f87171">Failed to connect to server.</span>');
        } finally {
            generateQuizBtn.disabled = false;
            generateQuizBtn.innerHTML = 'Generate Quiz';
        }
    });

    // Helper functions
    function addMessageToChat(role, content) {
        const id = 'msg-' + Math.random().toString(36).substr(2, 9);
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.id = id;
        msgDiv.innerHTML = content;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return id;
    }

    function addMessageToQuiz(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = content;
        quizBox.appendChild(msgDiv);
        quizBox.scrollTop = quizBox.scrollHeight;
    }

    // Simple markdown parser for bold, line breaks
    function parseMarkdown(text) {
        if (!text) return '';
        let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br>');
        return html;
    }
});
