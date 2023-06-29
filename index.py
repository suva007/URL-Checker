from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>URL Link Checker</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <style>
        body {
            background:  #333;
        }
        li{
            color: green;
            text-align: left;
            letter-spacing: 3px;
            line-height: 1.8;
        }
        h1 {
            color: green;
            line-height: 5;
            text-align: center;
            letter-spacing: 2.5px;
        }
        form{
            text-align:center;
        }
        input {
            width: 35%;
            margin-right: 20px;
            margin-bottom: 100px;
            font-size:18pt;
            height:40px;
        }
        button {
            width: 5%;
        }
        </style>
    </head>
    <body>
        <h1>URL LINK CHECKER</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

def check_link(url):
    try:
        response = requests.get(url)
        # Check if the response code is between 200 and 399 (success)
        if 200 <= response.status_code < 399:
            return True
        else:
            return False
    except:
        return False

@app.get("/")
async def get():
    # API that will launch inject the data to backend and will take data from backend to frontend.
    return HTMLResponse(html)

@app.get("/GET")
async def get(URL: str):
    # This API should return the list of links that are not working.
    try:
        code = requests.get(URL).status_code
    except:
        return "Not a Valid URL"
    return "Valid URL"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # This API will create the list of links and will populate to a common place for sharing with other API.
    await websocket.accept()
    while True:
        URL = await websocket.receive_text()
        
        if check_link(URL):
            response = requests.get(URL)
            soup = BeautifulSoup(response.text, 'html.parser')
            valid_links = ""
            invalid_links = ""
            for link in soup.find_all('a'):
                if check_link(link.get('href')):
                    valid_links += (link.get('href') + "\n")
                else:
                    invalid_links += (link.get('href') + "\n")
            await websocket.send_text(f"Valid URL: {valid_links}")
            await websocket.send_text(f"Not a Valid URL: {invalid_links}")
        else:
            await websocket.send_text(f"Not a valid URL: {URL}")