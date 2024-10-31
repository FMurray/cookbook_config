def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100):
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            while end > start and text[end] != " ":
                end -= 1
            if end == start:
                end = start + chunk_size
        else:
            end = len(text)

        chunks.append(text[start:end])
        start = end - overlap

        if start < 0:
            start = 0

    return chunks
