"""Phone call handling and Twilio integration."""

import logging
from typing import Optional

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from .config import settings
from .models import CallRecord, CallStatus

logger = logging.getLogger(__name__)


class PhoneHandler:
    """Handles incoming phone calls and Twilio integration."""

    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def is_mobile_number(self, phone_number: str) -> bool:
        """
        Check if the phone number is a mobile number.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if it's a valid mobile number
        """
        # Remove any formatting
        clean_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Check if it starts with allowed country codes
        for country_code in settings.allowed_country_codes:
            if clean_number.startswith(country_code):
                # Basic validation - mobile numbers are typically longer than landlines
                # This is a simplified check - in production, you'd use a proper phone validation service
                return len(clean_number) >= 10
        
        return False

    def handle_incoming_call(self, from_number: str, call_sid: str) -> VoiceResponse:
        """
        Handle an incoming call and generate TwiML response.
        
        Args:
            from_number: Caller's phone number
            call_sid: Twilio call SID
            
        Returns:
            TwiML response for the call
        """
        response = VoiceResponse()
        
        # Validate that it's a mobile number
        if not self.is_mobile_number(from_number):
            logger.warning(f"Rejected call from non-mobile number: {from_number}")
            response.say(
                "Sorry, this service is only available for mobile phone numbers. "
                "Please call from a mobile device.",
                voice="alice"
            )
            response.hangup()
            return response

        # Create call record
        call_record = CallRecord(
            call_sid=call_sid,
            from_number=from_number,
            to_number=settings.twilio_phone_number,
            status=CallStatus.RECORDING
        )
        
        # TODO: Store call record in database
        logger.info(f"Starting call recording for {from_number} (SID: {call_sid})")

        # Greet the caller and start recording
        response.say(
            "Welcome to TranscribeMe! Please speak your message after the beep. "
            "Your call will be transcribed and sent to you via text message. "
            "You have up to 5 minutes.",
            voice="alice"
        )
        
        # Start recording with webhook for when recording completes
        response.record(
            action=f"{settings.base_url}/webhook/recording",
            method="POST",
            max_length=settings.max_call_duration_seconds,
            play_beep=True,
            trim="trim-silence",
            recording_status_callback=f"{settings.base_url}/webhook/recording-status"
        )
        
        # Thank the caller
        response.say(
            "Thank you! Your message has been recorded and will be transcribed shortly. "
            "You'll receive a text message with your transcript.",
            voice="alice"
        )
        
        return response

    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS message to a phone number.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=settings.twilio_phone_number,
                to=to_number
            )
            logger.info(f"SMS sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return False

    def get_recording_url(self, call_sid: str) -> Optional[str]:
        """
        Get the recording URL for a completed call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Recording URL if found, None otherwise
        """
        try:
            recordings = self.client.recordings.list(call_sid=call_sid, limit=1)
            if recordings:
                return f"https://api.twilio.com{recordings[0].uri.replace('.json', '.mp3')}"
            return None
        except Exception as e:
            logger.error(f"Failed to get recording URL for call {call_sid}: {e}")
            return None