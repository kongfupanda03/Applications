########Background sharing references:
## https://stackoverflow.com/questions/71776967/sending-multiple-5mb-binary-files-over-ws-vs-http
## https://medium.com/platform-engineer/web-api-design-35df8167460
## uploading API using restful api
## chat/interaction using websoket

from fastapi import FastAPI, File, UploadFile, Form, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
from pydantic import BaseModel
import asyncio
import json
from fastapi.security.api_key import APIKeyHeader
from starlette.status import WS_1008_POLICY_VIOLATION

class QuestionRequest(BaseModel):
    question: str 

class FileInput(BaseModel):
    filename: List[str]
    filecontent: List[bytes]

VALID_API_KEYS = {"123"}

async def get_api_key_from_websocket(websocket: WebSocket):
    for header in websocket.headers.raw:
        print("hi")
        print(header[0].decode())
        print(header[1].decode())
        if header[0].decode().lower() == 'x-api-key':
            api_key = header[1].decode()
            if api_key in VALID_API_KEYS:
                return api_key
    return None

        

app = FastAPI()




@app.get("/")
async def main():
    return "This is the main page"

@app.post("/uploadfiles")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.websocket("/communicate")
async def websocket_endpoint(websocket: WebSocket):
    api_key = await get_api_key_from_websocket(websocket)
    if api_key is None:
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        return 
    await websocket.accept()  # Accept the WebSocket connection
    while True:
        try:
            # Receive text message from the client
            data = await websocket.receive_text()
            # Try to convert the text message into JSON
            payload = QuestionRequest.parse_raw(data)
            # Process the JSON payload
            # For example, you can send back a confirmation message
            response = {"message": "Payload received", "question": payload.dict()['question'],"answer":"dummy generated answer"}
            await websocket.send_json(response)
        except json.JSONDecodeError:
            # If error in decoding JSON, send an error message back to client
            await websocket.send_text("Error: Please send a valid JSON payload.")
        except Exception as e:
            # Close the connection if there's an error or if the client disconnects
            await websocket.close(code=1000)
            break



if __name__ == '__main__':
    app.run(debug=True)