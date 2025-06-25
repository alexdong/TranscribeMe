"""Data models for TranscribeMe service."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CallStatus(str, Enum):
    """Status of a transcription call."""

    INITIATED = "initiated"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptFormat(str, Enum):
    """Available transcript formatting options."""

    EMAIL = "email"
    NOTES = "notes"
    MEETING = "meeting"
    RAW = "raw"


class CallRecord(BaseModel):
    """Record of an incoming call and its processing."""

    call_sid: str = Field(..., description="Twilio call SID")
    from_number: str = Field(..., description="Caller's phone number")
    to_number: str = Field(..., description="Called number (our service)")
    status: CallStatus = Field(default=CallStatus.INITIATED)
    recording_url: str | None = Field(None, description="URL to the call recording")
    raw_transcript: str | None = Field(None, description="Raw transcription text")
    formatted_transcript: str | None = Field(
        None, description="AI-formatted transcript"
    )
    transcript_format: TranscriptFormat = Field(default=TranscriptFormat.NOTES)
    transcript_id: str | None = Field(
        None, description="Unique ID for hosted transcript"
    )
    sms_sent: bool = Field(default=False, description="Whether SMS was sent")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = Field(None, description="When transcript expires")
    error_message: str | None = Field(None, description="Error message if failed")


class TranscriptResponse(BaseModel):
    """Response model for transcript viewing."""

    id: str
    content: str
    format: TranscriptFormat
    created_at: datetime
    expires_at: datetime | None


class WebhookRequest(BaseModel):
    """Base model for Twilio webhook requests."""

    CallSid: str
    From: str
    To: str
    CallStatus: str


class VoiceWebhookRequest(WebhookRequest):
    """Model for Twilio voice webhook requests."""

    Direction: str
    ForwardedFrom: str | None = None
    CallerName: str | None = None


class RecordingWebhookRequest(BaseModel):
    """Model for Twilio recording webhook requests."""

    CallSid: str
    RecordingSid: str
    RecordingUrl: str
    RecordingStatus: str
    RecordingDuration: str
