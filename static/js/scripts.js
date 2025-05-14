document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('course-toggle');
    const level = document.getElementById('course-level');
    if (toggle && level) {
        toggle.addEventListener('change', () => {
            level.textContent = toggle.checked ? 'Secondary (6th to 10th)' : 'Primary (Nursery to 5th)';
            level.classList.toggle('text-yellow-300', toggle.checked);
            level.classList.toggle('text-blue-300', !toggle.checked);
        });
    }

    const quizOptions = document.querySelectorAll('.quiz-option');
    quizOptions.forEach(option => {
        option.addEventListener('click', async () => {
            const subject = option.textContent;
            const response = await fetch('/quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subject: subject })
            });
            const data = await response.json();
            document.getElementById('quiz-result').textContent = data.response;
        });
    });
});

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const container = document.getElementById('chat-container');
    const message = input.value;
    if (message) {
        container.innerHTML += `<p class="text-blue-800"><strong>You:</strong> ${message}</p>`;
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        container.innerHTML += `<p class="text-green-600"><strong>Bot:</strong> ${data.response}</p>`;
        container.scrollTop = container.scrollHeight;
        input.value = '';
    }
}

function handleChatEnter(e) {
    if (e.key === 'Enter') sendMessage();
}