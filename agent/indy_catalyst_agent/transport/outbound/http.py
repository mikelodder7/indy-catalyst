import logging

from aiohttp import ClientSession

from .message import OutboundMessage
from .base import BaseOutboundTransport
from .queue.base import BaseOutboundMessageQueue


class HttpTransport(BaseOutboundTransport):

    schemes = ("http", "https")

    def __init__(self, queue: BaseOutboundMessageQueue) -> None:
        self.logger = logging.getLogger(__name__)
        self._queue = queue

    async def __aenter__(self):
        self.client_session = ClientSession()
        return self

    async def __aexit__(self, *err):
        await self.client_session.close()
        self.client_session = None
        self.logger.error(err)

    @property
    def queue(self):
        return self._queue

    async def handle_message(self, message: OutboundMessage):
        try:
            headers = {}
            if isinstance(message.data, bytes):
                headers["Content-Type"] = "application/ssi-agent-wire"
            else:
                headers["Content-Type"] = "application/json"
            async with self.client_session.post(
                message.uri, data=message.data, headers=headers,
            ) as response:
                self.logger.info(response.status)
        except Exception:
            # TODO: add retry logic
            self.logger.exception("Error handling outbound message")
