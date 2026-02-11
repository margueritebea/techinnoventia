"""
WebSocket test with Django session authentication
"""
import requests
import websocket
import json
import http.cookiejar as cookielib

# 1. Login to get session cookie
session = requests.Session()

# Get CSRF token
response = session.get('http://localhost:8000/users/login/')
csrf_token = session.cookies.get('csrftoken', '')

# Login
login_data = {
    'username': 'admin',
    'password': 'Admin123!',
    'csrfmiddlewaretoken': csrf_token
}
response = session.post(
    'http://localhost:8000/users/login/',
    data=login_data,
    headers={'Referer': 'http://localhost:8000/users/login/'}
)

print(f"Login status: {response.status_code}")

# 2. Get cookies for WebSocket
cookies = session.cookies.get_dict()
cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

print(f"Cookies: {cookie_str[:100]}...")

# 3. Connect WebSocket with cookies
def on_message(ws, message):
    data = json.loads(message)
    print(f"[{data['type']}] {json.dumps(data, indent=2)}")

def on_error(ws, error):
    print(f"[ERROR] {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[CLOSED] {close_status_code}: {close_msg}")

def on_open(ws):
    print("[CONNECTED] ✓")
    
    # Send test message
    ws.send(json.dumps({
        'type': 'message',
        'content': 'Bonjour ! Peux-tu te présenter en une phrase ?'
    }))

# WebSocket connection with cookies
ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws/chat/",
    header=[f"Cookie: {cookie_str}"],
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

print("\n[CONNECTING] WebSocket...")
ws.run_forever()
