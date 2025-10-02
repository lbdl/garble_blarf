"""Transcription comparison and accuracy metrics."""

from collections import Counter
from typing import Dict, List, Tuple
import re
import math


def normalize_text(text: str, remove_punctuation: bool = True) -> str:
    """
    Normalize text for comparison.

    Args:
        text: Input text to normalize
        remove_punctuation: Whether to remove punctuation

    Returns:
        Normalized text string
    """
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation if requested
    if remove_punctuation:
        text = re.sub(r'[^\w\s]', '', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def calculate_wer(reference: str, hypothesis: str) -> Dict[str, float]:
    """
    Calculate Word Error Rate (WER) using Levenshtein distance.

    WER = (S + D + I) / N
    where S=substitutions, D=deletions, I=insertions, N=reference word count

    Args:
        reference: Ground truth transcription
        hypothesis: Transcription to evaluate

    Returns:
        Dict with wer, substitutions, deletions, insertions
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()

    # Build edit distance matrix
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]

    # Initialize first row and column
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    # Fill matrix
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    # Backtrack to count operation types
    i, j = len(ref_words), len(hyp_words)
    substitutions = deletions = insertions = 0

    while i > 0 or j > 0:
        if i == 0:
            insertions += 1
            j -= 1
        elif j == 0:
            deletions += 1
            i -= 1
        elif ref_words[i-1] == hyp_words[j-1]:
            i -= 1
            j -= 1
        else:
            # Find which operation was used
            options = []
            if i > 0 and j > 0:
                options.append((d[i-1][j-1], 'sub', i-1, j-1))
            if i > 0:
                options.append((d[i-1][j], 'del', i-1, j))
            if j > 0:
                options.append((d[i][j-1], 'ins', i, j-1))

            _, op, new_i, new_j = min(options)

            if op == 'sub':
                substitutions += 1
            elif op == 'del':
                deletions += 1
            else:
                insertions += 1

            i, j = new_i, new_j

    # Calculate WER
    n = len(ref_words)
    wer = (substitutions + deletions + insertions) / n if n > 0 else 0.0

    return {
        'wer': wer,
        'substitutions': substitutions,
        'deletions': deletions,
        'insertions': insertions,
        'total_edits': substitutions + deletions + insertions,
        'reference_words': n
    }


def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Calculate Character Error Rate (CER).

    Args:
        reference: Ground truth transcription
        hypothesis: Transcription to evaluate

    Returns:
        Character error rate (0.0 to 1.0+)
    """
    # Simple Levenshtein distance at character level
    ref_chars = list(reference)
    hyp_chars = list(hypothesis)

    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]

    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j

    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j-1] + 1,  # substitution
                            d[i][j-1] + 1,      # insertion
                            d[i-1][j] + 1)      # deletion

    n = len(ref_chars)
    return d[len(ref_chars)][len(hyp_chars)] / n if n > 0 else 0.0


def calculate_jaccard_similarity(reference: str, hypothesis: str) -> float:
    """
    Calculate Jaccard similarity (set-based word overlap).

    Args:
        reference: Ground truth transcription
        hypothesis: Transcription to evaluate

    Returns:
        Jaccard similarity (0.0 to 1.0)
    """
    ref_words = set(reference.split())
    hyp_words = set(hypothesis.split())

    if not ref_words and not hyp_words:
        return 1.0

    intersection = len(ref_words & hyp_words)
    union = len(ref_words | hyp_words)

    return intersection / union if union > 0 else 0.0


def calculate_cosine_similarity(reference: str, hypothesis: str) -> float:
    """
    Calculate cosine similarity (frequency-based).

    Args:
        reference: Ground truth transcription
        hypothesis: Transcription to evaluate

    Returns:
        Cosine similarity (0.0 to 1.0)
    """
    ref_counter = Counter(reference.split())
    hyp_counter = Counter(hypothesis.split())

    # Get all unique words
    all_words = set(ref_counter.keys()) | set(hyp_counter.keys())

    if not all_words:
        return 1.0

    # Build vectors
    ref_vec = [ref_counter.get(word, 0) for word in all_words]
    hyp_vec = [hyp_counter.get(word, 0) for word in all_words]

    # Calculate cosine similarity
    dot_product = sum(r * h for r, h in zip(ref_vec, hyp_vec))
    ref_magnitude = math.sqrt(sum(r * r for r in ref_vec))
    hyp_magnitude = math.sqrt(sum(h * h for h in hyp_vec))

    if ref_magnitude == 0 or hyp_magnitude == 0:
        return 0.0

    return dot_product / (ref_magnitude * hyp_magnitude)


def compare_transcriptions(
    reference_text: str,
    hypothesis_text: str,
    normalize: bool = True
) -> Dict[str, float]:
    """
    Compare two transcriptions with multiple accuracy metrics.

    Args:
        reference_text: Ground truth transcription
        hypothesis_text: Transcription to evaluate
        normalize: Whether to normalize text before comparison

    Returns:
        Dictionary with comparison metrics
    """
    # Normalize if requested
    if normalize:
        ref_normalized = normalize_text(reference_text)
        hyp_normalized = normalize_text(hypothesis_text)
    else:
        ref_normalized = reference_text
        hyp_normalized = hypothesis_text

    # Calculate all metrics
    wer_results = calculate_wer(ref_normalized, hyp_normalized)
    cer = calculate_cer(ref_normalized, hyp_normalized)
    jaccard = calculate_jaccard_similarity(ref_normalized, hyp_normalized)
    cosine = calculate_cosine_similarity(ref_normalized, hyp_normalized)

    # Word counts
    ref_word_count = len(ref_normalized.split())
    hyp_word_count = len(hyp_normalized.split())
    word_count_diff = hyp_word_count - ref_word_count
    word_count_diff_pct = (word_count_diff / ref_word_count * 100) if ref_word_count > 0 else 0.0

    return {
        'wer': wer_results['wer'],
        'cer': cer,
        'substitutions': wer_results['substitutions'],
        'deletions': wer_results['deletions'],
        'insertions': wer_results['insertions'],
        'total_edits': wer_results['total_edits'],
        'word_count_ref': ref_word_count,
        'word_count_hyp': hyp_word_count,
        'word_count_diff': word_count_diff,
        'word_count_diff_pct': word_count_diff_pct,
        'jaccard_similarity': jaccard,
        'cosine_similarity': cosine,
    }
