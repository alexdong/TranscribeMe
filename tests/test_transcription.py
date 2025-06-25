"""Tests for transcription service."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from transcribe_me.models import TranscriptFormat
from transcribe_me.transcription import TranscriptionService


class TestTranscriptionService:
    """Test cases for TranscriptionService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transcription_service = TranscriptionService()

    def test_format_transcript_email(self):
        """Test email formatting."""
        raw_text = "Hey this is a test message about the meeting tomorrow"

        with patch.object(
            self.transcription_service.client.chat.completions, "create"
        ) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "Subject: Meeting Tomorrow\n\nHi,\n\nThis is regarding the meeting tomorrow.\n\nBest regards"
            )
            mock_create.return_value = mock_response

            result = self.transcription_service.format_transcript(
                raw_text, TranscriptFormat.EMAIL
            )

            assert "Subject:" in result
            assert "Best regards" in result

    def test_format_transcript_notes(self):
        """Test notes formatting."""
        raw_text = "We need to buy groceries milk bread eggs and also call the dentist"

        with patch.object(
            self.transcription_service.client.chat.completions, "create"
        ) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "• Buy groceries:\n  - Milk\n  - Bread\n  - Eggs\n• Call the dentist"
            )
            mock_create.return_value = mock_response

            result = self.transcription_service.format_transcript(
                raw_text, TranscriptFormat.NOTES
            )

            assert "•" in result or "-" in result  # Should have bullet points

    def test_format_transcript_raw(self):
        """Test raw formatting (no changes)."""
        raw_text = "This is raw text that should not be changed"

        result = self.transcription_service.format_transcript(
            raw_text, TranscriptFormat.RAW
        )

        assert result == raw_text

    def test_format_transcript_api_failure(self):
        """Test formatting when API fails."""
        raw_text = "Test message"

        with patch.object(
            self.transcription_service.client.chat.completions, "create"
        ) as mock_create:
            mock_create.side_effect = Exception("API Error")

            result = self.transcription_service.format_transcript(
                raw_text, TranscriptFormat.EMAIL
            )

            # Should return raw text when formatting fails
            assert result == raw_text

    def test_generate_summary_short_text(self):
        """Test summary generation for text that's already short."""
        short_text = "This is a short message"

        result = self.transcription_service.generate_summary(short_text, 160)

        assert result == short_text

    def test_generate_summary_long_text(self):
        """Test summary generation for long text."""
        long_text = (
            "This is a very long message that exceeds the maximum length and needs to be summarized. "
            * 5
        )

        with patch.object(
            self.transcription_service.client.chat.completions, "create"
        ) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Long message summary"
            mock_create.return_value = mock_response

            result = self.transcription_service.generate_summary(long_text, 50)

            assert len(result) <= 50
            assert "Long message summary" in result

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        audio_url = "https://example.com/audio.mp3"

        with patch("httpx.AsyncClient") as mock_client:
            # Mock HTTP response
            mock_response = Mock()
            mock_response.content = b"fake audio data"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            # Mock OpenAI transcription
            with patch.object(
                self.transcription_service.client.audio.transcriptions, "create"
            ) as mock_transcribe:
                mock_transcribe.return_value = "This is the transcribed text"

                # Mock file operations
                with (
                    patch("tempfile.NamedTemporaryFile") as mock_temp,
                    patch("builtins.open", create=True) as mock_open,
                    patch("os.unlink") as mock_unlink,
                ):

                    mock_temp.return_value.__enter__.return_value.name = "/tmp/test.mp3"

                    result = await self.transcription_service.transcribe_audio(
                        audio_url
                    )

                    assert result == "This is the transcribed text"

    @pytest.mark.asyncio
    async def test_transcribe_audio_failure(self):
        """Test audio transcription failure."""
        audio_url = "https://example.com/audio.mp3"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Network error")
            )

            result = await self.transcription_service.transcribe_audio(audio_url)

            assert result is None
