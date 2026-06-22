// 風雲客棧 Main JS

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.4)';
            } else {
                navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.3)';
            }
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Auto-dismiss flash messages after 5 seconds (skip persistent alerts)
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Animate elements on scroll (Intersection Observer)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .feature-card, .aiot-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    const chatbot = document.getElementById('chatbotWidget');
    if (chatbot) {
        const panel = document.getElementById('chatbotPanel');
        const toggle = document.getElementById('chatbotToggle');
        const closeBtn = document.getElementById('chatbotClose');
        const clearBtn = document.getElementById('chatbotClear');
        const form = document.getElementById('chatbotForm');
        const input = document.getElementById('chatbotInput');
        const sendBtn = document.getElementById('chatbotSend');
        const messages = document.getElementById('chatbotMessages');
        const chatApi = chatbot.dataset.chatApi;
        const clearApi = chatbot.dataset.clearApi;

        const addMessage = (text, kind = 'bot') => {
            const row = document.createElement('div');
            row.className = `chatbot-message ${kind}`;

            const bubble = document.createElement('div');
            bubble.className = 'chatbot-bubble';
            bubble.textContent = text;

            row.appendChild(bubble);
            messages.appendChild(row);
            messages.scrollTop = messages.scrollHeight;
            return row;
        };

        const setOpen = (open) => {
            chatbot.classList.toggle('open', open);
            panel.setAttribute('aria-hidden', String(!open));
            toggle.setAttribute('aria-expanded', String(open));
            toggle.setAttribute('aria-label', open ? '關閉聊天' : '開啟聊天');
            toggle.innerHTML = open ? '<i class="bi bi-x-lg"></i>' : '<i class="bi bi-chat-dots-fill"></i>';
            if (open) {
                setTimeout(() => input.focus(), 120);
            }
        };

        const setBusy = (busy) => {
            input.disabled = busy;
            sendBtn.disabled = busy;
        };

        toggle.addEventListener('click', () => {
            setOpen(!chatbot.classList.contains('open'));
        });

        closeBtn.addEventListener('click', () => setOpen(false));

        clearBtn.addEventListener('click', async () => {
            try {
                await fetch(clearApi, { method: 'POST' });
            } catch (error) {
                addMessage(`清除失敗：${error.message}`, 'error');
                return;
            }
            messages.replaceChildren();
            addMessage('對話已清除。');
            input.focus();
        });

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const message = input.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            input.value = '';
            setBusy(true);
            const loading = addMessage('回覆中...', 'bot loading');

            try {
                const response = await fetch(chatApi, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                const data = await response.json();
                loading.remove();

                if (response.ok) {
                    addMessage(data.reply || '目前沒有回覆。');
                } else {
                    addMessage(data.error || '呼叫失敗，請稍後再試。', 'error');
                }
            } catch (error) {
                loading.remove();
                addMessage(`連線失敗：${error.message}`, 'error');
            } finally {
                setBusy(false);
                input.focus();
            }
        });
    }
});
