"""Integration tests for SMS functionality."""

from unittest.mock import Mock, patch

from transcribe_me.config import settings
from transcribe_me.phone_handler import PhoneHandler


class TestSMSIntegration:
    """Integration tests for SMS sending functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.phone_handler = PhoneHandler()

    def test_nz_mobile_validation(self):
        """Test New Zealand mobile number validation."""
        # Valid NZ mobile numbers
        valid_numbers = [
            "+64210822348",  # Test number
            "+6421-082-2348",  # With dashes
            "+64 21 082 2348",  # With spaces
            "+64(21)0822348",  # With brackets
            "+64211234567",  # Different prefix
            "+64271234567",  # Vodafone
            "+64221234567",  # 2degrees
        ]

        for number in valid_numbers:
            assert self.phone_handler.is_mobile_number(
                number
            ), f"Should accept {number}"
            print(f"✅ Accepted NZ mobile: {number}")

    def test_non_nz_mobile_rejection(self):
        """Test rejection of non-NZ mobile numbers."""
        invalid_numbers = [
            "+15551234567",  # US
            "+447123456789",  # UK
            "+61412345678",  # Australia
            "+33123456789",  # France
            "0210822348",  # No country code
            "+64123456",  # Too short
            "+6409123456789",  # Landline (09 area code)
            "+6403123456789",  # Landline (03 area code)
        ]

        for number in invalid_numbers:
            assert not self.phone_handler.is_mobile_number(
                number
            ), f"Should reject {number}"
            print(f"❌ Rejected non-NZ mobile: {number}")

    @patch("transcribe_me.phone_handler.Client")
    def test_sms_sending_success(self, mock_client):
        """Test successful SMS sending to NZ mobile."""
        # Mock successful SMS response
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "queued"
        mock_client.return_value.messages.create.return_value = mock_message

        # Test SMS to NZ mobile
        test_number = settings.test_mobile_number
        test_message = "Test SMS from TranscribeMe integration test"

        handler = PhoneHandler()
        result = handler.send_sms(test_number, test_message)

        assert result is True
        mock_client.return_value.messages.create.assert_called_once_with(
            body=test_message, from_=settings.twilio_phone_number, to=test_number
        )
        print(f"✅ SMS test successful to {test_number}")

    @patch("transcribe_me.phone_handler.Client")
    def test_sms_sending_failure(self, mock_client):
        """Test SMS sending failure handling."""
        # Mock SMS failure
        mock_client.return_value.messages.create.side_effect = Exception(
            "Twilio API Error"
        )

        handler = PhoneHandler()
        result = handler.send_sms("+64210822348", "Test message")

        assert result is False
        print("✅ SMS failure handling works correctly")

    @patch("transcribe_me.phone_handler.Client")
    def test_sms_content_formatting(self, mock_client):
        """Test SMS content formatting and length."""
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "queued"
        mock_client.return_value.messages.create.return_value = mock_message

        handler = PhoneHandler()

        # Test different message lengths
        test_cases = [
            ("Short message", "Short message"),
            ("A" * 160, "A" * 160),  # Standard SMS length
            ("A" * 500, "A" * 500),  # Long message (should still work)
        ]

        for description, message in test_cases:
            result = handler.send_sms("+64210822348", message)
            assert result is True
            print(
                f"✅ SMS formatting test passed: {description} ({len(message)} chars)"
            )

    def test_twiml_generation_nz_mobile(self):
        """Test TwiML generation for valid NZ mobile."""
        response = self.phone_handler.handle_incoming_call(
            "+64210822348", "test_call_sid"
        )
        response_str = str(response)

        # Check TwiML contains expected elements
        checks = [
            ("Welcome to TranscribeMe" in response_str, "Welcome message"),
            ("<Record" in response_str, "Record element"),
            ("New Zealand" in response_str, "NZ-specific message"),
            ("Thank you" in response_str, "Thank you message"),
            ("<Hangup" not in response_str, "No hangup for valid number"),
        ]

        for check, description in checks:
            assert check, f"TwiML check failed: {description}"
            print(f"✅ TwiML check passed: {description}")

    def test_twiml_generation_non_nz_mobile(self):
        """Test TwiML generation for invalid non-NZ mobile."""
        response = self.phone_handler.handle_incoming_call(
            "+15551234567", "test_call_sid"
        )
        response_str = str(response)

        # Check TwiML contains rejection elements
        checks = [
            (
                "Sorry, this service is only available for New Zealand" in response_str,
                "NZ-only message",
            ),
            ("<Hangup" in response_str, "Hangup for invalid number"),
            ("<Record" not in response_str, "No record for invalid number"),
        ]

        for check, description in checks:
            assert check, f"TwiML rejection check failed: {description}"
            print(f"✅ TwiML rejection check passed: {description}")


if __name__ == "__main__":
    # Run tests directly
    test_sms = TestSMSIntegration()
    test_sms.setup_method()

    print("🧪 Running SMS Integration Tests...")

    test_sms.test_nz_mobile_validation()
    test_sms.test_non_nz_mobile_rejection()
    test_sms.test_twiml_generation_nz_mobile()
    test_sms.test_twiml_generation_non_nz_mobile()

    print("✅ All SMS integration tests passed!")
