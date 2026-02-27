const avatarElement = document.getElementById('avatar');

let ws;
const RELOAD_INTERVAL = 2000;

function connect() {
    // Construct websocket URL relative to current host
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/avatar`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("Connected to AI Orchestrator WebSocket");
        avatarElement.className = "idle";
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log("State change:", data.state);
            if (['idle', 'thinking', 'talking'].includes(data.state)) {
                avatarElement.className = data.state;
            }
        } catch (e) {
            console.error("Failed to parse websocket message", e);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 2s...");
        avatarElement.className = "idle"; // Fallback state
        setTimeout(connect, RELOAD_INTERVAL);
    };

    ws.onerror = (err) => {
        console.error("WebSocket encountered error: ", err, "Closing socket");
        ws.close();
    };
}

// Initial connection
connect();
