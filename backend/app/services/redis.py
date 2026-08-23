"""Async Redis connection manager."""

from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from app.core.config import Settings
from app.core.opentelemetry import start_span


class RedisManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client: Redis | None = None

    async def connect(self) -> None:
        self.client = Redis.from_url(
            self.settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    async def ping(self) -> bool:
        if self.client is None:
            return False
        with start_span("Redis connectivity check", **{"db.system": "redis", "db.operation": "PING"}) as span:
            try:
                # A short socket preflight keeps the health endpoint deterministic
                # when the host-mapped Redis service is not running.
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.settings.redis_host, self.settings.redis_port),
                    timeout=1.0,
                )
                writer.close()
                await writer.wait_closed()
                result = bool(await asyncio.wait_for(self.client.ping(), timeout=1.5))
                if span is not None:
                    span.set_attribute("eos.check.status", "healthy" if result else "unhealthy")
                return result
            except Exception as error:
                if span is not None:
                    span.record_exception(error)
                    span.set_attribute("eos.check.status", "unhealthy")
                return False

    async def disconnect(self) -> None:
        if self.client is not None:
            client = self.client
            self.client = None
            # Detach the client before closing it so shutdown remains
            # non-blocking even if a failed health-check left a socket task
            # waiting on a remote host.
            try:
                await asyncio.wait_for(client.aclose(), timeout=0.25)
            except Exception:
                pass
