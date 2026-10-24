def split_summary(text):
    """Split text into nonblank messages of at most 2,000 UTF-16 units.

    Prefer paragraph, line, and word boundaries, in that order. Counting
    non-BMP characters as two units also keeps emoji-heavy messages safe.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start
        length = 0
        while end < len(text):
            character_length = 2 if ord(text[end]) > 0xFFFF else 1
            if length + character_length > 2000:
                break
            length += character_length
            end += 1

        if end < len(text):
            for separator in ('\n\n', '\n', ' '):
                boundary = text.rfind(separator, start, end)
                if boundary > start:
                    end = boundary + len(separator)
                    break

        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end

    return chunks
