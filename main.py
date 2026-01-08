import uvicorn
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pre_processing import PreProcessor, UserInput
from log_call import LogCall
from log_new_task import LogTask
from log_email import LogEmail, EmailInput
from next_action import NextAction


app = FastAPI(
    title="PCG Toolkit API",
    version="1.0.0",
    description="FollowThru API",
    contact={
        "name": "Greggory Rodgers",
        "email": "greggrodgers.ii@gmail.com",
    },
)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI() # expects OPENAI_API_KEY in env

# Endpionts

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # OpenAI Whisper API
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=(file.filename, file.file, file.content_type)
        )
        return {"transcription": transcription.text}
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/processes")
def process(user_input: UserInput):
    processor = PreProcessor(user_input)
    result = processor.pre_processing_output()
    return result

@app.post("/log_call")
def log_call(user_input: UserInput):
    try:
        logging_call = LogCall(user_input)
        result = logging_call.log_call_output()
        return result
    except Exception as e:
        print(f"Error in /log_call: {e}")
        return {
            "subject": "Error processing call",
            "comments": f"An error occurred: {str(e)}. Please check the logs or try again.",
            "error": True
        }

@app.post("/log_task")
def task_call(user_input: UserInput):
    try:
        logging_task = LogTask(user_input)
        result = logging_task.log_task_output()
        return result
    except Exception as e:
        print(f"Error in /log_task: {e}")
        return {
            "subject": "Error processing task",
            "comments": f"An error occurred: {str(e)}",
            "error": True
        }

@app.post("/log_email")
def log_email(payload: EmailInput):
    try:
        return LogEmail(payload).log_email_output()
    except Exception as e:
        print(f"Error in /log_email: {e}")
        return {
            "subject": "Error processing email",
            "body": f"An error occurred: {str(e)}",
            "error": True
        }

@app.post("/next_action")
def next_action(user_input: UserInput):
    try:
        next_action_creation = NextAction(user_input)
        result = next_action_creation.next_action_output()
        return result
    except Exception as e:
        print(f"Error in /next_action: {e}")
        return {
             "next_actions": [{"action": "Error", "description": f"An error occurred: {str(e)}"}],
             "error": True
        }



# ... existing imports ...
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ... existing app definition ...

# ... allow CORS ...

# ... existing API endpoints ...

# Serve React Frontend (Deployment)
# Only mount if the dist folder exists (i.e., we are in production/deployed mode)
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    # Catch-all for SPA to serve index.html
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Allow API calls to pass through if they weren't caught above (though API routes defined *before* this will catch first)
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Check if file exists in root of dist (e.g. favicon.ico, logo)
        file_path = os.path.join("frontend/dist", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
             return FileResponse(file_path)

        # distinct fallback to index.html for SPA routing
        return FileResponse("frontend/dist/index.html")