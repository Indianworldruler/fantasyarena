import asyncio
import logging
from collections import defaultdict
from typing import Callable, Any

logger = logging.getLogger("event_bus")


class EventBus:
    """
    Lightweight in-process pub/sub event bus.

    Design Pattern: Observer
    In production this would be replaced by Apache Kafka or Redis Pub/Sub
    for cross-service communication at scale.

    Topics:
        match.event      - raw match event (wicket, run, goal, etc.)
        scoring.updated  - team scores have been recomputed
        leaderboard.updated - leaderboard has been re-ranked
        notification.send   - a notification must be dispatched
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable):
        self._subscribers[topic].append(handler)
        logger.info(f"Subscribed handler '{handler.__name__}' to topic '{topic}'")

    async def publish(self, topic: str, payload: Any):
        logger.info(f"Publishing to '{topic}': {payload}")
        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as exc:
                logger.error(f"Handler '{handler.__name__}' failed on topic '{topic}': {exc}")


bus = EventBus()
