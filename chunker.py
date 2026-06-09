"""
Chunking Strategy Implementation
- Chunk size: ~512 tokens (~350-400 words)
- Overlap: 50-75 characters
- Source: scraped_results.txt (food places near CSUF)
"""

import re
import json

# ── helpers ──────────────────────────────────────────────────────────────────

def word_count(text):
    return len(text.split())

def clean_text(text):
    """Remove HTML artifacts, extra whitespace, and junk lines."""
    # Remove HTML artifacts
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-z]+;|&#\d+;', "'", text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing whitespace per line
    text = '\n'.join(line.rstrip() for line in text.splitlines())
    return text.strip()

def chunk_text(text, source_name, target_words=375, overlap_chars=62):
    """
    Splits text into overlapping chunks.
    target_words  ≈ 375  (midpoint of 350-400)
    overlap_chars ≈ 62   (midpoint of 50-75)
    Returns list of dicts with metadata.
    """
    # Tokenise into sentences (keep delimiter)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_words = []
    current_chars = 0
    chunk_index = 0

    for sentence in sentences:
        sw = sentence.split()
        # If adding this sentence would exceed the target, flush first
        if current_chars > 0 and current_words and (current_chars + len(sentence) + 1) / 5 > target_words:
            chunk_text_str = ' '.join(current_words)
            chunks.append({
                "chunk_id": f"{source_name}_chunk_{chunk_index:03d}",
                "source": source_name,
                "word_count": word_count(chunk_text_str),
                "text": chunk_text_str
            })
            chunk_index += 1

            # Overlap: carry last ~overlap_chars characters worth of words into next chunk
            overlap_text = chunk_text_str[-overlap_chars:]
            # Trim to a word boundary
            space_idx = overlap_text.find(' ')
            if space_idx != -1:
                overlap_text = overlap_text[space_idx:].strip()
            current_words = overlap_text.split() if overlap_text else []
            current_chars = len(' '.join(current_words))

        current_words.extend(sw)
        current_chars += len(sentence) + 1

    # Flush remaining
    if current_words:
        chunk_text_str = ' '.join(current_words)
        if word_count(chunk_text_str) > 20:   # skip tiny trailing fragments
            chunks.append({
                "chunk_id": f"{source_name}_chunk_{chunk_index:03d}",
                "source": source_name,
                "word_count": word_count(chunk_text_str),
                "text": chunk_text_str
            })

    return chunks


# ── parse scraped_results.txt into per-source blocks ─────────────────────────

def parse_sources(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Split on the separator lines
    blocks = re.split(r'={60,}', raw)
    sources = {}

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Extract LINK N label and domain
        link_match = re.match(r'LINK\s+(\d+):\s+(https?://\S+)', block)
        domain_match = re.search(r'Domain\s*:\s*(\S+)', block)
        if not link_match:
            continue

        link_num = link_match.group(1)
        url      = link_match.group(2)
        domain   = domain_match.group(1) if domain_match else 'unknown'

        # Skip error / login-wall / JS-only blocks
        if re.search(r'ERROR:|requires login|requires JavaScript|static scraping unavailable', block):
            continue

        # Strip the header lines to get just content
        content_lines = []
        for line in block.splitlines():
            if re.match(r'LINK\s+\d+:|Domain\s*:|^-{20,}', line):
                continue
            content_lines.append(line)

        content = clean_text('\n'.join(content_lines))
        if len(content.split()) < 30:   # skip nearly-empty blocks
            continue

        # Derive a short slug for chunk IDs
        slug = re.sub(r'[^a-z0-9]+', '_', domain.lower().replace('www.', ''))
        slug = f"link{link_num}_{slug}"

        sources[slug] = {"url": url, "domain": domain, "content": content}

    return sources


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    input_path  = 'scraped_results.txt'
    output_path = 'chunks.json'

    sources = parse_sources(input_path)
    print(f"Sources with usable content: {len(sources)}")

    all_chunks = []
    for slug, meta in sources.items():
        source_chunks = chunk_text(meta['content'], slug)
        for c in source_chunks:
            c['url'] = meta['url']
        all_chunks.extend(source_chunks)
        print(f"  {slug}: {len(source_chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")

    # ── Print 5 representative chunks ────────────────────────────────────────
    print("\n" + "="*70)
    print("5 REPRESENTATIVE CHUNKS (quality inspection)")
    print("="*70)
    step = max(1, len(all_chunks) // 5)
    sample_indices = [0, step, step*2, step*3, len(all_chunks)-1]
    for idx in sample_indices[:5]:
        c = all_chunks[idx]
        print(f"\n--- {c['chunk_id']} ({c['word_count']} words) ---")
        print(c['text'][:600])
        print("...")

    # ── Save ──────────────────────────────────────────────────────────────────
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_chunks)} chunks → {output_path}")


if __name__ == '__main__':
    main()
