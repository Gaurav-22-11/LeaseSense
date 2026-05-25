from leasesense.chunking import chunk_text


def test_chunk_text_preserves_content_order():
    text = "A first clause about rent.\n\nA second clause about subleasing.\n\nA third clause."

    chunks = chunk_text(text, chunk_size=45, overlap=0)

    assert len(chunks) >= 2
    joined = " ".join(chunk.text for chunk in chunks)
    assert "first clause" in joined
    assert "subleasing" in joined
    assert chunks[0].index == 0

