"""Transcription and AI formatting services."""

import logging

from openai import OpenAI

from .config import settings
from .models import TranscriptFormat

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Handles audio transcription and AI formatting."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def transcribe_audio(self, audio_url: str) -> str | None:
        """
        Transcribe audio from URL using OpenAI Whisper.

        Args:
            audio_url: URL to the audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            # Download audio file
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                audio_data = response.content

            # Save temporarily for Whisper API
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Transcribe using Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="text"
                )

            # Clean up temp file
            import os

            os.unlink(temp_file_path)

            logger.info(f"Successfully transcribed audio from {audio_url}")
            return transcript

        except Exception as e:
            logger.error(f"Failed to transcribe audio from {audio_url}: {e}")
            return None

    def format_transcript(self, raw_text: str, format_type: TranscriptFormat) -> str:
        """
        Format raw transcript using AI.

        Args:
            raw_text: Raw transcribed text
            format_type: Desired formatting style

        Returns:
            Formatted transcript
        """
        prompts = {
            TranscriptFormat.EMAIL: (
                "Format this transcribed voice message as a professional email. "
                "Add an appropriate subject line and structure it with proper paragraphs. "
                "Correct any grammar issues and make it sound professional:\n\n"
            ),
            TranscriptFormat.NOTES: (
                "Format this transcribed voice message as clear, organized notes. "
                "Use bullet points, proper headings, and structure it for easy reading. "
                "Correct grammar and spelling:\n\n"
            ),
            TranscriptFormat.MEETING: (
                "Format this transcribed voice message as meeting minutes. "
                "Organize into sections like Discussion Points, Decisions Made, and Action Items. "
                "Make it professional and well-structured:\n\n"
            ),
            TranscriptFormat.RAW: "",
        }

        if format_type == TranscriptFormat.RAW:
            return raw_text

        try:
            prompt = prompts[format_type] + raw_text

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional assistant that formats transcribed voice messages. "
                        "Always maintain the original meaning while improving clarity and structure.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            formatted_text = response.choices[0].message.content.strip()
            logger.info(f"Successfully formatted transcript with {format_type} style")
            return formatted_text

        except Exception as e:
            logger.error(f"Failed to format transcript: {e}")
            # Return raw text if formatting fails
            return raw_text

    def generate_summary(self, text: str, max_length: int = 160) -> str:
        """
        Generate a short summary for SMS.

        Args:
            text: Full transcript text
            max_length: Maximum length for SMS

        Returns:
            Short summary
        """
        if len(text) <= max_length:
            return text

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Create a brief summary of this text in {max_length} characters or less. "
                        "Keep the key points and make it clear and concise.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=50,
                temperature=0.3,
            )

            summary = response.choices[0].message.content.strip()
            return summary[:max_length]

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Return truncated text if summarization fails
            return text[:max_length] + "..." if len(text) > max_length else text
