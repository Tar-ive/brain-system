"""Test cases for Gmail tools implementation."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from gmail_arcade_mcp.gmail_tools import GmailTools
from gmail_arcade_mcp.config import GmailArcadeConfig


class TestGmailSendEmail:
    """Test cases for Gmail send email functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GmailArcadeConfig(
            arcade_api_key="arc_test_key_12345",
            user_id="tarive22@gmail.com",
            rate_limit_requests=100,
            rate_limit_window=3600,
            timeout_seconds=30,
            max_retries=3,
            retry_delay=1.0
        )

    @pytest.fixture
    def gmail_tools(self, config):
        """Create Gmail tools instance."""
        return GmailTools(config)

    @pytest.mark.asyncio
    async def test_send_email_to_target_recipient(self, gmail_tools):
        """
        Test: Send email to pqo14@txstate.edu with subject 'test'
        Expected: Email successfully delivered with confirmation
        """
        # Arrange
        recipient = "pqo14@txstate.edu"
        subject = "test"
        body = "Test email from Gmail-Arcade MCP server"

        # Mock Arcade client and responses
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {
            "message": "Email sent successfully",
            "message_id": "test_message_id_123"
        }
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.send_email(
            recipient=recipient,
            subject=subject,
            body=body
        )

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["metadata"]["tool"] == "gmail_send_email"

        # Verify Arcade API was called correctly
        mock_client.tools.authorize.assert_called_once_with(
            tool_name="Gmail.SendEmail",
            user_id="tarive22@gmail.com"
        )
        mock_client.tools.execute.assert_called_once()

        # Verify parameters were passed correctly
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["tool_name"] == "Gmail.SendEmail"
        assert call_args[1]["input"]["recipient"] == recipient
        assert call_args[1]["input"]["subject"] == subject
        assert call_args[1]["input"]["body"] == body

    @pytest.mark.asyncio
    async def test_email_parameter_validation_invalid_recipient(self, gmail_tools):
        """Test: Validate email parameters - invalid recipient format"""
        # Act & Assert
        with pytest.raises(ValueError, match="Email validation failed"):
            await gmail_tools.send_email(
                recipient="invalid-email",
                subject="test",
                body="test body"
            )

    @pytest.mark.asyncio
    async def test_email_parameter_validation_missing_subject(self, gmail_tools):
        """Test: Validate email parameters - missing subject"""
        # Act & Assert
        with pytest.raises(ValueError, match="Email validation failed"):
            await gmail_tools.send_email(
                recipient="test@example.com",
                subject="",
                body="test body"
            )

    @pytest.mark.asyncio
    async def test_email_parameter_validation_missing_body(self, gmail_tools):
        """Test: Validate email parameters - missing body"""
        # Act & Assert
        with pytest.raises(ValueError, match="Email validation failed"):
            await gmail_tools.send_email(
                recipient="test@example.com",
                subject="test",
                body=""
            )

    @pytest.mark.asyncio
    async def test_email_with_cc_and_bcc(self, gmail_tools):
        """Test: Send email with CC and BCC recipients"""
        # Arrange
        recipient = "pqo14@txstate.edu"
        subject = "test"
        body = "Test email with CC and BCC"
        cc = ["cc1@example.com", "cc2@example.com"]
        bcc = ["bcc1@example.com"]

        # Mock Arcade client
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"message": "Email sent successfully"}
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.send_email(
            recipient=recipient,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc
        )

        # Assert
        assert result["success"] is True

        # Verify CC and BCC were included in the API call
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["input"]["cc"] == cc
        assert call_args[1]["input"]["bcc"] == bcc

    @pytest.mark.asyncio
    async def test_authentication_required_flow(self, gmail_tools):
        """Test: Handle authentication required scenario"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "pending"
        mock_auth_response.url = "https://arcade.ai/auth/123"
        mock_client.tools.authorize.return_value = mock_auth_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.send_email(
            recipient="test@example.com",
            subject="test",
            body="test body"
        )

        # Assert
        assert result["success"] is False
        assert "Authentication required" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_arcade_api_error_handling(self, gmail_tools):
        """Test: Handle Arcade API errors gracefully"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response
        mock_client.tools.execute.side_effect = Exception("API rate limit exceeded")

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.send_email(
            recipient="test@example.com",
            subject="test",
            body="test body"
        )

        # Assert
        assert result["success"] is False
        assert "API rate limit exceeded" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_email_content_sanitization(self, gmail_tools):
        """Test: Ensure email content is sanitized"""
        # Arrange
        malicious_subject = "Test <script>alert('xss')</script>"
        malicious_body = "Hello <script>alert('xss')</script> World"

        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"message": "Email sent successfully"}
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.send_email(
            recipient="test@example.com",
            subject=malicious_subject,
            body=malicious_body
        )

        # Assert
        assert result["success"] is True

        # Verify content was sanitized
        call_args = mock_client.tools.execute.call_args
        sanitized_subject = call_args[1]["input"]["subject"]
        sanitized_body = call_args[1]["input"]["body"]

        assert "<script>" not in sanitized_subject
        assert "<script>" not in sanitized_body


class TestGmailListEmails:
    """Test cases for Gmail list emails functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GmailArcadeConfig(
            arcade_api_key="arc_test_key_12345",
            user_id="tarive22@gmail.com"
        )

    @pytest.fixture
    def gmail_tools(self, config):
        """Create Gmail tools instance."""
        return GmailTools(config)

    @pytest.mark.asyncio
    async def test_list_emails_default_count(self, gmail_tools):
        """Test: List emails with default count"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {
            "emails": [
                {"subject": "Test 1", "sender": "test1@example.com"},
                {"subject": "Test 2", "sender": "test2@example.com"}
            ]
        }
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.list_emails()

        # Assert
        assert result["success"] is True
        assert "data" in result

        # Verify API call
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["input"]["n_emails"] == 5  # Default value

    @pytest.mark.asyncio
    async def test_list_emails_custom_count(self, gmail_tools):
        """Test: List emails with custom count"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"emails": []}
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.list_emails(n_emails=10)

        # Assert
        assert result["success"] is True

        # Verify API call
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["input"]["n_emails"] == 10

    @pytest.mark.asyncio
    async def test_list_emails_count_clamping(self, gmail_tools):
        """Test: Email count is clamped to valid range"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"emails": []}
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Test upper bound clamping
        result = await gmail_tools.list_emails(n_emails=100)
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["input"]["n_emails"] == 50  # Clamped to max

        # Test lower bound clamping
        result = await gmail_tools.list_emails(n_emails=0)
        call_args = mock_client.tools.execute.call_args
        assert call_args[1]["input"]["n_emails"] == 1  # Clamped to min


class TestGmailWhoAmI:
    """Test cases for Gmail who am I functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GmailArcadeConfig(
            arcade_api_key="arc_test_key_12345",
            user_id="tarive22@gmail.com"
        )

    @pytest.fixture
    def gmail_tools(self, config):
        """Create Gmail tools instance."""
        return GmailTools(config)

    @pytest.mark.asyncio
    async def test_who_am_i_success(self, gmail_tools):
        """Test: Get user profile information successfully"""
        # Arrange
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {
            "email": "tarive22@gmail.com",
            "name": "Test User"
        }
        mock_client.tools.execute.return_value = mock_execute_response

        gmail_tools.client = mock_client

        # Act
        result = await gmail_tools.who_am_i()

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["metadata"]["tool"] == "gmail_who_am_i"

        # Verify API call
        mock_client.tools.execute.assert_called_once_with(
            tool_name="Gmail.WhoAmI",
            input={},
            user_id="tarive22@gmail.com"
        )