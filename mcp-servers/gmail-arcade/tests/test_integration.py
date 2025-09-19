"""Integration tests for Gmail-Arcade MCP server."""

import pytest
import os
import asyncio
from unittest.mock import patch, Mock
from gmail_arcade_mcp.server import GmailArcadeMCPServer
from gmail_arcade_mcp.config import load_config, GmailArcadeConfig


class TestEmailIntegration:
    """Integration tests for email functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        return GmailArcadeConfig(
            arcade_api_key="arc_test_key_12345",
            user_id="tarive22@gmail.com",
            rate_limit_requests=100,
            rate_limit_window=3600,
            timeout_seconds=30,
            max_retries=3,
            retry_delay=1.0
        )

    @pytest.mark.asyncio
    async def test_send_email_to_target_recipient_end_to_end(self, mock_config):
        """
        Integration Test: Send email to pqo14@txstate.edu with subject 'test'
        This is the primary test case specified in the requirements.
        """
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        # Mock the arcade-gmail send_email function
        mock_send_email_result = {
            "success": True,
            "message": "Email sent successfully to pqo14@txstate.edu",
            "message_id": "integration_test_message_id",
            "recipient": "pqo14@txstate.edu",
            "subject": "test",
            "timestamp": "2025-09-14T10:00:00Z"
        }

        # Patch arcade-gmail send_email function
        with patch('gmail_arcade_mcp.gmail_tools.arcade_send_email', return_value=mock_send_email_result) as mock_send:
            await server.initialize()

            # Act - Call the tool through the server
            result = await server._call_tool(
                name="gmail_send_email",
                arguments={
                    "recipient": "pqo14@txstate.edu",
                    "subject": "test",
                    "body": "Integration test email from Gmail-Arcade MCP server"
                }
            )

            # Assert
            assert len(result) == 1
            assert result[0].type == "text"

            # Parse the result text (it should be a string representation of the result dict)
            result_text = result[0].text
            assert "success" in result_text.lower()
            assert "true" in result_text.lower()  # success: True

            # Verify that the arcade_send_email function was called with correct parameters
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args.kwargs["recipient"] == "pqo14@txstate.edu"
            assert call_args.kwargs["subject"] == "test"
            assert "Integration test email" in call_args.kwargs["body"]

    @pytest.mark.asyncio
    async def test_complete_workflow_lifecycle(self, mock_config):
        """
        Test: Complete workflow lifecycle from tool listing to execution
        This tests the complete MCP server workflow as it would be used by Claude.
        """
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        # Mock Arcade client
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"success": True, "message": "Email sent"}
        mock_client.tools.execute.return_value = mock_execute_response

        with patch('gmail_arcade_mcp.gmail_tools.Arcade', return_value=mock_client):
            await server.initialize()

            # Act 1: List available tools
            tools = await server._list_tools()

            # Assert 1: Verify tools are available
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "gmail_send_email",
                "gmail_list_emails",
                "gmail_who_am_i",
                "gmail_search_emails",
                "gmail_write_draft_email",
                "gmail_send_draft_email"
            ]

            for expected_tool in expected_tools:
                assert expected_tool in tool_names

            # Act 2: Execute send email tool
            result = await server._call_tool(
                name="gmail_send_email",
                arguments={
                    "recipient": "test@example.com",
                    "subject": "Integration Test",
                    "body": "Complete workflow test"
                }
            )

            # Assert 2: Verify execution
            assert len(result) == 1
            assert result[0].type == "text"
            assert "success" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_config):
        """Test: Error handling in integration scenarios"""
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        # Mock Arcade client with authentication failure
        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "pending"
        mock_auth_response.url = "https://arcade.ai/auth/test"
        mock_client.tools.authorize.return_value = mock_auth_response

        with patch('gmail_arcade_mcp.gmail_tools.Arcade', return_value=mock_client):
            await server.initialize()

            # Act: Try to send email when authentication is required
            result = await server._call_tool(
                name="gmail_send_email",
                arguments={
                    "recipient": "test@example.com",
                    "subject": "Error Test",
                    "body": "This should fail due to authentication"
                }
            )

            # Assert: Error is handled gracefully
            assert len(result) == 1
            assert result[0].type == "text"
            result_text = result[0].text.lower()
            assert "success" in result_text
            assert "false" in result_text  # success: False

    @pytest.mark.asyncio
    async def test_multiple_tool_executions(self, mock_config):
        """Test: Multiple tool executions in sequence"""
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        # Mock different responses for different tools
        mock_execute_responses = [
            Mock(output=Mock(value={"profile": "user_profile"})),  # who_am_i
            Mock(output=Mock(value={"emails": ["email1", "email2"]})),  # list_emails
            Mock(output=Mock(value={"success": True, "message_id": "123"}))  # send_email
        ]
        mock_client.tools.execute.side_effect = mock_execute_responses

        with patch('gmail_arcade_mcp.gmail_tools.Arcade', return_value=mock_client):
            await server.initialize()

            # Act: Execute multiple tools
            # 1. Get user profile
            result1 = await server._call_tool("gmail_who_am_i", {})

            # 2. List emails
            result2 = await server._call_tool("gmail_list_emails", {"n_emails": 3})

            # 3. Send email
            result3 = await server._call_tool(
                "gmail_send_email",
                {
                    "recipient": "test@example.com",
                    "subject": "Multi-tool test",
                    "body": "Testing multiple tool executions"
                }
            )

            # Assert: All tools executed successfully
            for result in [result1, result2, result3]:
                assert len(result) == 1
                assert result[0].type == "text"
                assert "success" in result[0].text.lower()

            # Verify all tools were called
            assert mock_client.tools.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_parameter_validation_integration(self, mock_config):
        """Test: Parameter validation in integration context"""
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        with patch('gmail_arcade_mcp.gmail_tools.Arcade'):
            await server.initialize()

            # Act: Try to send email with invalid parameters
            result = await server._call_tool(
                name="gmail_send_email",
                arguments={
                    "recipient": "invalid-email-format",  # Invalid email
                    "subject": "Test",
                    "body": "Test body"
                }
            )

            # Assert: Validation error is handled
            assert len(result) == 1
            assert result[0].type == "text"
            result_text = result[0].text.lower()
            assert "success" in result_text
            assert "false" in result_text  # success: False
            assert "validation" in result_text or "invalid" in result_text


class TestConfigurationIntegration:
    """Integration tests for configuration loading."""

    def test_config_loading_with_env_file(self):
        """Test: Configuration loading from environment file"""
        # Arrange - Create temporary env file
        test_env_content = """
ARCADE_API_KEY=arc_test_integration_key_12345
GMAIL_USER_ID=test-integration@gmail.com
GMAIL_RATE_LIMIT_REQUESTS=200
GMAIL_TIMEOUT_SECONDS=45
        """.strip()

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(test_env_content)
            temp_env_path = f.name

        try:
            # Act
            config = load_config(temp_env_path)

            # Assert
            assert config.arcade_api_key == "arc_test_integration_key_12345"
            assert config.user_id == "test-integration@gmail.com"
            assert config.rate_limit_requests == 200
            assert config.timeout_seconds == 45

        finally:
            # Cleanup
            os.unlink(temp_env_path)

    def test_config_validation_integration(self):
        """Test: Configuration validation in integration context"""
        # Test invalid API key
        with pytest.raises(ValueError, match="Invalid Arcade API key format"):
            GmailArcadeConfig(
                arcade_api_key="invalid_key_format",
                user_id="test@gmail.com"
            )

        # Test invalid user ID
        with pytest.raises(ValueError, match="Invalid user ID format"):
            GmailArcadeConfig(
                arcade_api_key="arc_valid_key_123",
                user_id="invalid_user_id_format"
            )


class TestBrainSystemIntegration:
    """Integration tests for brain system compatibility."""

    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance(self, mock_config):
        """Test: MCP protocol compliance for brain system integration"""
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        with patch('gmail_arcade_mcp.gmail_tools.Arcade'):
            await server.initialize()

            # Act: Test tool listing (required for MCP discovery)
            tools = await server._list_tools()

            # Assert: Tools follow MCP specification
            for tool in tools:
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'inputSchema')
                assert isinstance(tool.inputSchema, dict)
                assert 'type' in tool.inputSchema
                assert 'properties' in tool.inputSchema

    @pytest.mark.asyncio
    async def test_response_format_compatibility(self, mock_config):
        """Test: Response format compatibility with brain system expectations"""
        # Arrange
        server = GmailArcadeMCPServer(mock_config)

        mock_client = Mock()
        mock_auth_response = Mock()
        mock_auth_response.status = "completed"
        mock_client.tools.authorize.return_value = mock_auth_response

        mock_execute_response = Mock()
        mock_execute_response.output.value = {"success": True}
        mock_client.tools.execute.return_value = mock_execute_response

        with patch('gmail_arcade_mcp.gmail_tools.Arcade', return_value=mock_client):
            await server.initialize()

            # Act
            result = await server._call_tool(
                name="gmail_send_email",
                arguments={
                    "recipient": "test@example.com",
                    "subject": "Brain System Test",
                    "body": "Testing brain system compatibility"
                }
            )

            # Assert: Response format is compatible
            assert len(result) == 1
            assert hasattr(result[0], 'type')
            assert hasattr(result[0], 'text')
            assert result[0].type == "text"
            assert isinstance(result[0].text, str)