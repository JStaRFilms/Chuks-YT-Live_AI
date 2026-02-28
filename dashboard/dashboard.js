document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatFeed = document.getElementById('chat-feed');
    const queueList = document.getElementById('queue-list');
    const queueCount = document.getElementById('queue-count');
    const statSession = document.getElementById('stat-session');
    const statPinned = document.getElementById('stat-pinned');
    const avatarBadge = document.getElementById('avatar-state-badge');
    const avatarContainer = document.querySelector('.avatar-preview-container');
    const avatarImg = document.getElementById('avatar-img');

    // Status indicators
    const statusMic = document.getElementById('status-mic');
    const statusGroq = document.getElementById('status-groq');
    const statusKokoro = document.getElementById('status-kokoro');

    // State Tracking
    let messageIds = new Set();

    // Connect WebSocket
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("Dashboard WebSocket Connected");
        };

        ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                if (payload.type === 'full_state') {
                    updateDashboard(payload.data);
                }
            } catch (e) {
                console.error("Failed to parse WS message", e);
            }
        };

        ws.onclose = () => {
            console.warn("WebSocket closed. Attempting reconnect in 2s...");
            setTimeout(connectWebSocket, 2000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket encountered an error", err);
            ws.close();
        };
    }

    // Initial Fetch (Fallback)
    async function fetchInitialState() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            updateDashboard(data);
        } catch (e) {
            console.error("Failed to fetch initial state", e);
        }
    }

    // Update UI
    function updateDashboard(state) {
        // 1. Update Session / Memory Stats
        statSession.textContent = state.session.session_id || "None";
        statPinned.textContent = state.session.pinned_count || "0";

        // 2. Update Queue
        queueCount.textContent = `${state.queue.size}/${state.queue.max}`;
        queueList.innerHTML = '';
        if (state.queue.items.length === 0) {
            queueList.innerHTML = '<li class="empty-state">Queue is empty</li>';
        } else {
            state.queue.items.forEach(item => {
                const li = document.createElement('li');
                li.className = 'queue-item';
                li.textContent = item;
                queueList.appendChild(li);
            });
        }

        // 3. Update Avatar State
        const avatarState = state.avatar_state || 'idle';
        avatarBadge.textContent = avatarState.toUpperCase();

        // Reset classes
        avatarContainer.classList.remove('state-idle', 'state-thinking', 'state-talking');
        avatarContainer.classList.add(`state-${avatarState}`);

        // 4. Update Conversation Feed
        if (state.history && state.history.length > 0) {
            // Remove empty state text
            const emptyState = chatFeed.querySelector('.empty-state');
            if (emptyState) emptyState.remove();

            // Rebuild feed if items count differs or just append. 
            // For simplicity in a small list, we can just rebuild it cleanly.
            chatFeed.innerHTML = '';

            state.history.forEach(msg => {
                const isUser = msg.role === 'user';
                const msgEl = document.createElement('div');
                msgEl.className = `message ${isUser ? 'msg-user' : 'msg-ai'}`;

                const label = document.createElement('div');
                label.className = 'msg-label';
                label.textContent = isUser ? 'Streamer' : 'Chuks';

                const bubble = document.createElement('div');
                bubble.className = 'msg-bubble';
                bubble.textContent = msg.content;

                msgEl.appendChild(label);
                msgEl.appendChild(bubble);
                chatFeed.appendChild(msgEl);
            });

            // Scroll to bottom
            chatFeed.scrollTop = chatFeed.scrollHeight;
        }

        // 5. Update Status Bar
        if (!state.status.mic_active) statusMic.classList.add('offline');
        else statusMic.classList.remove('offline');

        if (!state.status.groq_api) statusGroq.classList.add('offline');
        else statusGroq.classList.remove('offline');

        if (!state.status.kokoro_api) statusKokoro.classList.add('offline');
        else statusKokoro.classList.remove('offline');
    }

    // Init
    fetchInitialState().then(connectWebSocket);
});
