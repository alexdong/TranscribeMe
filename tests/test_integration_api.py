"""Integration tests for API endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from transcribe_me.main import app


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data

        print(f"✅ Health endpoint working: {data}")

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "TranscribeMe"
        assert "New Zealand" in data["description"]
        assert data["supported_countries"] == ["+64"]

        print(f"✅ Root endpoint working: {data}")

    def test_voice_webhook_valid_nz_mobile(self):
        """Test voice webhook with valid NZ mobile number."""
        response = self.client.post(
            "/webhook/voice",
            data={
                "CallSid": "test_call_nz_123",
                "From": "+64210822348",
                "To": "+64123456789",
                "CallStatus": "ringing",
            },
        )

        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]

        # Check TwiML content
        twiml_content = response.text
        assert "Welcome to TranscribeMe" in twiml_content
        assert "<Record" in twiml_content
        assert "New Zealand" in twiml_content

        print("✅ Voice webhook accepts valid NZ mobile")

    def test_voice_webhook_invalid_mobile(self):
        """Test voice webhook with invalid mobile number."""
        response = self.client.post(
            "/webhook/voice",
            data={
                "CallSid": "test_call_invalid_123",
                "From": "+15551234567",  # US number
                "To": "+64123456789",
                "CallStatus": "ringing",
            },
        )

        assert response.status_code == 200

        # Check TwiML content for rejection
        twiml_content = response.text
        assert "Sorry, this service is only available for New Zealand" in twiml_content
        assert "<Hangup" in twiml_content

        print("✅ Voice webhook rejects invalid mobile")

    def test_recording_webhook(self):
        """Test recording webhook."""
        # First create a call record
        self.client.post(
            "/webhook/voice",
            data={
                "CallSid": "test_call_recording_123",
                "From": "+64210822348",
                "To": "+64123456789",
                "CallStatus": "ringing",
            },
        )

        # Mock the transcription process
        with patch("transcribe_me.main.process_transcription") as mock_process:
            mock_process.return_value = None

            response = self.client.post(
                "/webhook/recording",
                data={
                    "CallSid": "test_call_recording_123",
                    "RecordingUrl": "https://api.twilio.com/test-recording.mp3",
                    "RecordingDuration": "45",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"

            print("✅ Recording webhook working")

    def test_admin_calls_endpoint(self):
        """Test admin calls endpoint."""
        # Create some test call records first
        self.client.post(
            "/webhook/voice",
            data={
                "CallSid": "admin_test_call_1",
                "From": "+64210822348",
                "To": "+64123456789",
                "CallStatus": "ringing",
            },
        )

        response = self.client.get("/admin/calls")

        assert response.status_code == 200
        data = response.json()
        assert "calls" in data
        assert len(data["calls"]) >= 1

        # Check call record structure
        call = data["calls"][0]
        assert "call_sid" in call
        assert "from_number" in call
        assert "status" in call

        print(f"✅ Admin endpoint working: {len(data['calls'])} calls found")

    def test_transcript_not_found(self):
        """Test transcript endpoint with invalid ID."""
        response = self.client.get("/transcript/nonexistent-id")

        assert response.status_code == 404

        print("✅ Transcript 404 handling working")

    def test_error_handling_malformed_webhook(self):
        """Test error handling for malformed webhook data."""
        # Missing required fields
        response = self.client.post(
            "/webhook/voice",
            data={
                "CallSid": "test_malformed",
                # Missing From, To, CallStatus
            },
        )

        assert response.status_code == 422  # Validation error

        print("✅ Malformed webhook data handled correctly")

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import time

        def make_request(i):
            return self.client.get("/health")

        start_time = time.time()

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

        print(
            f"✅ Concurrent requests handled: 10 requests in {end_time - start_time:.2f}s"
        )


if __name__ == "__main__":
    # Run tests directly
    test_api = TestAPIIntegration()

    print("🧪 Running API Integration Tests...")

    test_api.setup_method()
    test_api.test_health_endpoint()
    test_api.test_root_endpoint()
    test_api.test_voice_webhook_valid_nz_mobile()
    test_api.test_voice_webhook_invalid_mobile()
    test_api.test_recording_webhook()
    test_api.test_admin_calls_endpoint()
    test_api.test_transcript_not_found()
    test_api.test_error_handling_malformed_webhook()
    test_api.test_concurrent_requests()

    print("✅ All API integration tests passed!")
