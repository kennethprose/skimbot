import re
from datetime import datetime, timedelta, timezone


def duration_start(value, now):
    """Return the UTC start of a duration ending at the command invocation."""
    match = re.fullmatch(r'([0-9]+)\s*([mhd])', value.strip(), re.IGNORECASE)
    if match is None:
        raise ValueError('Use a positive duration such as 30m, 4h, or 2d.')
    try:
        amount = int(match[1])
        if amount <= 0:
            raise ValueError('Duration must be greater than zero.')
        seconds = amount * {'m': 60, 'h': 3600, 'd': 86400}[match[2].lower()]
        return now.astimezone(timezone.utc) - timedelta(seconds=seconds)
    except OverflowError:
        raise ValueError('That duration is too large. Try a shorter duration.') from None


def parse_since(value, now):
    """Parse a past ISO 8601 timestamp with an explicit timezone into UTC."""
    example = (
        'Use a timestamp with a timezone, such as '
        '2026-10-24T09:00:00-04:00 or 2026-10-24T13:00:00Z.'
    )
    try:
        timestamp = datetime.fromisoformat(value.strip())
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError
        timestamp = timestamp.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError(example) from None
    if timestamp >= now:
        raise ValueError('The start time must be earlier than this command.')
    return timestamp


def resolve_selection(now, *, duration=None, count=None, since=None):
    """Validate exactly one slash-command option and resolve its history bounds."""
    if sum(value is not None for value in (duration, count, since)) != 1:
        raise ValueError(
            'Choose exactly one option: count, duration, or since. '
            'For example, /skim count:20 or /skim duration:30m.'
        )
    if count is not None:
        if count <= 0:
            raise ValueError('Message count must be greater than zero.')
        return {'count': count}
    if duration is not None:
        return {'after': duration_start(duration, now)}
    return {'after': parse_since(since, now)}


async def collect_messages(channel, *, before, after=None, count=None):
    """Collect human messages within fixed bounds, returned oldest first."""
    if count is not None and count <= 0:
        raise ValueError('Message count must be greater than zero.')
    messages = []
    async for message in channel.history(
        limit=None,
        before=before,
        after=after,
        oldest_first=count is None,
    ):
        if message.author.bot or message.created_at >= before:
            continue
        if after is not None and message.created_at <= after:
            continue
        messages.append(message)
        if count is not None and len(messages) >= count:
            break
    return sorted(messages, key=lambda message: (message.created_at, message.id))
