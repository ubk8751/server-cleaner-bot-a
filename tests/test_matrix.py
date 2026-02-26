import pytest
from unittest.mock import Mock, AsyncMock
from catcord_bots.matrix import MatrixSession


class TestMatrix:
    @pytest.mark.asyncio
    async def test_session_close(self):
        mock_api = Mock()
        mock_api.session = AsyncMock()
        mock_api.session.close = AsyncMock()
        session = MatrixSession(api=mock_api, client=Mock())
        await session.close()
        mock_api.session.close.assert_called_once()
