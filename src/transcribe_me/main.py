"""Main FastAPI application for TranscribeMe service."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse

from .config import settings
from .models import CallRecord, CallStatus, TranscriptFormat, TranscriptResponse
from .phone_handler import PhoneHandler
from .transcription import TranscriptionService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TranscribeMe",
    description="Phone-based transcription service",
    version="0.1.0"
)

# Initialize services
phone_handler = PhoneHandler()
transcription_service = TranscriptionService()

# In-memory storage for demo (replace with database in production)
call_records: Dict[str, CallRecord] = {}
transcripts: Dict[str, TranscriptResponse] = {}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "TranscribeMe",
        "version": "0.1.0",
        "description": "Phone-based transcription service",
        "phone_number": settings.twilio_phone_number
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/webhook/voice")
async def handle_voice_webhook(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle incoming voice calls from Twilio."""
    logger.info(f"Voice webhook: {CallSid} from {From} to {To}, status: {CallStatus}")
    
    # Generate TwiML response for the call
    twiml_response = phone_handler.handle_incoming_call(From, CallSid)
    
    # Store call record
    call_records[CallSid] = CallRecord(
        call_sid=CallSid,
        from_number=From,
        to_number=To,
        status=CallStatus.RECORDING
    )
    
    return PlainTextResponse(str(twiml_response), media_type="application/xml")


@app.post("/webhook/recording")
async def handle_recording_webhook(
    request: Request,
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(...)
):
    """Handle recording completion from Twilio."""
    logger.info(f"Recording webhook: {CallSid}, URL: {RecordingUrl}, Duration: {RecordingDuration}")
    
    # Update call record
    if CallSid in call_records:
        call_record = call_records[CallSid]
        call_record.recording_url = RecordingUrl
        call_record.status = CallStatus.TRANSCRIBING
        
        # Start transcription process (in background)
        await process_transcription(call_record)
    
    return {"status": "received"}


async def process_transcription(call_record: CallRecord):
    """Process transcription and send SMS (background task)."""
    try:
        # Transcribe audio
        raw_transcript = await transcription_service.transcribe_audio(call_record.recording_url)
        if not raw_transcript:
            raise Exception("Transcription failed")
        
        call_record.raw_transcript = raw_transcript
        call_record.status = CallStatus.FORMATTING
        
        # Format transcript
        formatted_transcript = transcription_service.format_transcript(
            raw_transcript, 
            call_record.transcript_format
        )
        call_record.formatted_transcript = formatted_transcript
        
        # Generate unique transcript ID and store
        transcript_id = str(uuid.uuid4())
        call_record.transcript_id = transcript_id
        call_record.expires_at = datetime.utcnow() + timedelta(days=settings.transcript_expiry_days)
        
        # Store transcript for web viewing
        transcripts[transcript_id] = TranscriptResponse(
            id=transcript_id,
            content=formatted_transcript,
            format=call_record.transcript_format,
            created_at=call_record.created_at,
            expires_at=call_record.expires_at
        )
        
        # Generate SMS message
        summary = transcription_service.generate_summary(formatted_transcript, 100)
        transcript_url = f"{settings.base_url}/transcript/{transcript_id}"
        
        sms_message = (
            f"Your transcript is ready!\\n\\n"
            f"Preview: {summary}\\n\\n"
            f"Full transcript: {transcript_url}\\n\\n"
            f"Expires: {call_record.expires_at.strftime('%Y-%m-%d')}"
        )
        
        # Send SMS
        sms_sent = phone_handler.send_sms(call_record.from_number, sms_message)
        call_record.sms_sent = sms_sent
        call_record.status = CallStatus.COMPLETED
        
        logger.info(f"Successfully processed transcription for call {call_record.call_sid}")
        
    except Exception as e:
        logger.error(f"Failed to process transcription for call {call_record.call_sid}: {e}")
        call_record.status = CallStatus.FAILED
        call_record.error_message = str(e)


@app.get("/transcript/{transcript_id}")
async def view_transcript(transcript_id: str):
    """View a hosted transcript."""
    if transcript_id not in transcripts:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    transcript = transcripts[transcript_id]
    
    # Check if expired
    if transcript.expires_at and datetime.utcnow() > transcript.expires_at:
        del transcripts[transcript_id]
        raise HTTPException(status_code=410, detail="Transcript has expired")
    
    # Return HTML page for viewing
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TranscribeMe - Transcript</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }}
            .transcript {{ background: #f9f9f9; padding: 20px; border-radius: 5px; line-height: 1.6; }}
            .meta {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
            .copy-btn {{ background: #007bff; color: white; border: none; padding: 10px 20px; 
                        border-radius: 5px; cursor: pointer; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>TranscribeMe</h1>
            <p>Your voice message transcript</p>
        </div>
        
        <div class="transcript">
            <pre style="white-space: pre-wrap; font-family: inherit;">{transcript.content}</pre>
        </div>
        
        <button class="copy-btn" onclick="copyToClipboard()">Copy to Clipboard</button>
        
        <div class="meta">
            <p><strong>Format:</strong> {transcript.format.value}</p>
            <p><strong>Created:</strong> {transcript.created_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
            {f'<p><strong>Expires:</strong> {transcript.expires_at.strftime("%Y-%m-%d %H:%M UTC")}</p>' if transcript.expires_at else ''}
        </div>
        
        <script>
            function copyToClipboard() {{
                const text = document.querySelector('.transcript pre').textContent;
                navigator.clipboard.writeText(text).then(() => {{
                    alert('Transcript copied to clipboard!');
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/admin/calls")
async def list_calls():
    """Admin endpoint to list all calls (for debugging)."""
    return {"calls": list(call_records.values())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)