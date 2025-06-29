"""Tests for phone handler functionality."""

from unittest.mock import Mock, patch

from transcribe_me.phone_handler import PhoneHandler


class TestPhoneHandler:
    """Test cases for PhoneHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.phone_handler = PhoneHandler()

    def test_is_mobile_number_valid_nz(self):
        """Test mobile number validation for NZ numbers."""
        assert self.phone_handler.is_mobile_number("+64210822348")
        assert self.phone_handler.is_mobile_number("+64 21 082 2348")
        assert self.phone_handler.is_mobile_number("+64-21-082-2348")
        assert self.phone_handler.is_mobile_number("+64211234567")
        assert self.phone_handler.is_mobile_number("+64271234567")
        assert self.phone_handler.is_mobile_number("+64221234567")

    def test_is_mobile_number_invalid(self):
        """Test mobile number validation for invalid numbers."""
        assert not self.phone_handler.is_mobile_number("+15551234567")  # US not allowed
        assert not self.phone_handler.is_mobile_number("+447123456789")  # UK not allowed
        assert not self.phone_handler.is_mobile_number("+33123456789")  # France not allowed
        assert not self.phone_handler.is_mobile_number("0210822348")  # No country code
        assert not self.phone_handler.is_mobile_number("+64123456")  # Too short

    def test_handle_incoming_call_valid_mobile(self):
        """Test handling incoming call from valid NZ mobile number."""
        response = self.phone_handler.handle_incoming_call(
            "+64210822348", "test_call_sid"
        )

        # Check that response contains expected TwiML elements
        response_str = str(response)
        assert "Welcome to TranscribeMe" in response_str
        assert "<Record" in response_str
        assert "Thank you" in response_str

    def test_handle_incoming_call_invalid_mobile(self):
        """Test handling incoming call from invalid mobile number."""
        response = self.phone_handler.handle_incoming_call(
            "+33123456789", "test_call_sid"
        )

        # Check that response rejects the call
        response_str = str(response)
        assert (
            "Sorry, this service is only available for New Zealand mobile phone numbers"
            in response_str
        )
        assert "<Hangup" in response_str

    @patch("transcribe_me.phone_handler.Client")
    def test_send_sms_success(self, mock_client):
        """Test successful SMS sending."""
        # Mock Twilio client
        mock_message = Mock()
        mock_message.sid = "test_message_sid"
        mock_client.return_value.messages.create.return_value = mock_message

        # Create new handler with mocked client
        handler = PhoneHandler()

        result = handler.send_sms("+64210822348", "Test message")

        assert result is True

    @patch("transcribe_me.phone_handler.Client")
    def test_send_sms_failure(self, mock_client):
        """Test SMS sending failure."""
        # Mock Twilio client to raise exception
        mock_client.return_value.messages.create.side_effect = Exception("API Error")

        # Create new handler with mocked client
        handler = PhoneHandler()

        result = handler.send_sms("+64210822348", "Test message")

        assert result is False
