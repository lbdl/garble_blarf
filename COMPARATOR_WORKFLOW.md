# Comparator Workflow - Model Comparison Testing

## Overview

The `comparator` tool allows you to transcribe the same voice memo with multiple models and compare their accuracy against a reference (ground truth) transcription.

## Test Memos Selected

1. **"Studying In Samui"**
   - UUID: `76050490-57EF-4D3D-B8DC-8D31B149F7BA`
   - Duration: 4.5 seconds
   - Current (Apple): "Hambrook Sao Payung Evian beauty movie"

2. **"31 Long Acre"**
   - UUID: `6E03852D-6283-48AF-B1A2-FB1A93DE9ABD`
   - Duration: 10.1 seconds
   - Current (Apple): "Religious change as corporate buyout between various gods buying each other's franchises"

## Complete Workflow

### Step 1: Transcribe with Multiple Models

Transcribe each memo with the models you want to compare:

```bash
# Transcribe first memo
comparator transcribe-models 76050490-57EF-4D3D-B8DC-8D31B149F7BA \
  --models whisper-base,faster-whisper-base

# Transcribe second memo
comparator transcribe-models 6E03852D-6283-48AF-B1A2-FB1A93DE9ABD \
  --models whisper-base,faster-whisper-base
```

**Available models:**
- `apple` (already have this from original transcription)
- `whisper-base`
- `faster-whisper-base`
- `whisper-small`
- `faster-whisper-small`
- `whisper-medium`
- `faster-whisper-medium`
- etc.

### Step 2: View All Transcriptions

List all model transcriptions for a memo to see what each model produced:

```bash
# View transcriptions for memo 1
comparator list-transcriptions 76050490-57EF-4D3D-B8DC-8D31B149F7BA

# View transcriptions for memo 2
comparator list-transcriptions 6E03852D-6283-48AF-B1A2-FB1A93DE9ABD
```

This shows:
- Model name
- Transcription ID (needed for setting reference)
- Status (success/failed)
- Processing time
- Word count
- Preview of transcription text

### Step 3: Set Reference (Ground Truth)

After listening to the audio and determining the correct transcription, set it as the reference:

**Option A: Type the correct transcription manually**

```bash
comparator set-reference 76050490-57EF-4D3D-B8DC-8D31B149F7BA \
  --text "the actual correct transcription here"
```

**Option B: Mark an existing model transcription as reference** (if one is already correct)

```bash
comparator set-reference 76050490-57EF-4D3D-B8DC-8D31B149F7BA --id <transcription-id>
```

The transcription ID is shown in the `list-transcriptions` output.

### Step 4: Compare All Models

Run comparison of all model transcriptions against your reference:

```bash
# Compare for memo 1
comparator compare-all 76050490-57EF-4D3D-B8DC-8D31B149F7BA

# Compare for memo 2
comparator compare-all 6E03852D-6283-48AF-B1A2-FB1A93DE9ABD
```

This calculates and stores:
- **WER** (Word Error Rate) - lower is better
- **CER** (Character Error Rate)
- Edit operations (substitutions, deletions, insertions)
- Word count differences
- Jaccard similarity (vocabulary overlap)
- Cosine similarity (frequency-based)

### Step 5: View Results

Display the comparison results, ranked by accuracy:

```bash
# View results for memo 1
comparator show-results 76050490-57EF-4D3D-B8DC-8D31B149F7BA

# View results for memo 2
comparator show-results 6E03852D-6283-48AF-B1A2-FB1A93DE9ABD
```

Output shows:
- Models ranked by WER (best to worst)
- 🏆 emoji for best performer
- All accuracy metrics for each model

## Understanding Metrics

### Word Error Rate (WER)
- **Primary metric** for speech recognition accuracy
- Lower is better (0% = perfect, 100% = completely wrong)
- Industry standard for ASR evaluation
- Calculated as: `(Substitutions + Deletions + Insertions) / Total Words`

### Character Error Rate (CER)
- Like WER but at character level
- Useful for catching minor spelling differences
- Lower is better

### Jaccard Similarity
- Measures vocabulary overlap (set-based)
- Range: 0.0 to 1.0 (1.0 = perfect match)
- Ignores word order and frequency

### Cosine Similarity
- Measures word frequency similarity (vector-based)
- Range: 0.0 to 1.0 (1.0 = perfect match)
- Accounts for word repetition

## Example Full Workflow

```bash
# 1. Transcribe with multiple models
comparator transcribe-models 76050490-57EF-4D3D-B8DC-8D31B149F7BA \
  --models whisper-base,faster-whisper-base

# 2. View what each model produced
comparator list-transcriptions 76050490-57EF-4D3D-B8DC-8D31B149F7BA

# 3. Set your corrected reference transcription
comparator set-reference 76050490-57EF-4D3D-B8DC-8D31B149F7BA \
  --text "Hamburg south Phuket Evian Beauty Movie"

# 4. Run comparison
comparator compare-all 76050490-57EF-4D3D-B8DC-8D31B149F7BA

# 5. See which model won
comparator show-results 76050490-57EF-4D3D-B8DC-8D31B149F7BA
```

## Tips

1. **Start with short memos** (like the two selected) for quick testing
2. **Listen carefully** to create accurate reference transcriptions
3. **Test multiple memos** to get statistically meaningful results
4. **Compare similar durations** - some models perform better on short vs long audio
5. **Note processing time** - faster-whisper models should be ~4x faster than regular whisper

## Database Structure

The comparator uses separate tables from the main transcription system:

- **`model_transcriptions`** - Stores multiple model outputs per memo
- **`transcription_comparisons`** - Stores comparison metrics
- Original `transcriptions` table remains intact with Apple transcriptions

## Next Steps

After testing these two memos:

1. Expand to more test cases (different lengths, accents, content types)
2. Build a test set of 10-20 memos with reference transcriptions
3. Run comprehensive comparison across all models
4. Identify best model for your use case
5. Document model performance statistics

## Quick Reference Commands

```bash
# Get help
comparator --help
comparator transcribe-models --help

# List available models
memo-transcriber list-models

# View existing transcriptions in main database
memo-transcriber list-cached --compact --limit 20
```
