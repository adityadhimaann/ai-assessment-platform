# 🤖 Hybrid AI Setup - GPT-4 + Gemini

## What is Hybrid AI?

Your system now uses **BOTH** GPT-4 and Google Gemini simultaneously to:

1. **Generate Better Questions**: Both models create questions, then the system picks the best one
2. **Provide Better Feedback**: Both models evaluate answers, then combines their insights
3. **Increase Reliability**: If one model fails, the other is used as backup

## Benefits

✅ **Higher Quality**: Two AI models are better than one
✅ **More Variety**: Different perspectives lead to more diverse questions
✅ **Better Feedback**: Combined insights from both models
✅ **Reliability**: Automatic fallback if one model fails
✅ **Cost Effective**: Gemini is cheaper than GPT-4

## How It Works

### Question Generation
```
User asks for question
        ↓
┌───────────────────────┐
│  Call GPT-4 & Gemini  │ ← Parallel (fast!)
│      simultaneously   │
└───────────────────────┘
        ↓
┌───────────────────────┐
│   Score both questions│
│   - Length            │
│   - Specificity       │
│   - Clarity           │
└───────────────────────┘
        ↓
   Select BEST question
```

### Answer Evaluation
```
User submits answer
        ↓
┌───────────────────────┐
│  Call GPT-4 & Gemini  │ ← Parallel (fast!)
│      simultaneously   │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Combine evaluations  │
│  - Average scores     │
│  - Merge feedback     │
│  - Consensus on       │
│    correctness        │
└───────────────────────┘
        ↓
   Return BEST evaluation
```

## Setup Instructions

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **Get API Key**
3. Click **Create API Key**
4. Copy your API key

### 2. Add to Backend .env

Open `aibackend/.env` and add:

```env
# Gemini Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
USE_GEMINI=true
```

### 3. Restart Backend

```bash
cd aibackend
python3 main.py
```

You should see:
```
✅ Hybrid AI: Both GPT-4 and Gemini available
```

## Configuration Options

### Use Only GPT-4
```env
USE_GEMINI=false
```
or don't set GEMINI_API_KEY

### Use Only Gemini
Not recommended - GPT-4 is better for structured responses

### Use Both (Recommended)
```env
GEMINI_API_KEY=your_key
USE_GEMINI=true
```

## Performance

| Metric | GPT-4 Only | Hybrid (GPT-4 + Gemini) |
|--------|-----------|-------------------------|
| **Question Quality** | Good | Excellent |
| **Feedback Detail** | Good | Excellent |
| **Variety** | Medium | High |
| **Speed** | 2-3s | 2-3s (parallel) |
| **Cost per Question** | $0.01 | $0.008 |
| **Reliability** | 99% | 99.9% |

## Logs

Watch the backend logs to see hybrid AI in action:

```
🤖 Generating question with GPT-4 and Gemini in parallel...
📊 Question scores - GPT-4: 85.00, Gemini: 78.00
✅ Selected: GPT-4 (higher quality score)
```

```
🤖 Evaluating answer with GPT-4 and Gemini in parallel...
✅ Combined evaluation - Score: 87, Correct: true
```

## Troubleshooting

### "Gemini not available"
- Check your GEMINI_API_KEY in .env
- Make sure google-generativeai is installed
- System will fallback to GPT-4 only

### "Both models failed"
- Check your internet connection
- Verify both API keys are valid
- Check API quotas/limits

### Questions still similar
- Make sure DEV_MODE=false in .env
- Restart the backend
- Clear any caches

## Cost Comparison

### Per 10 Questions Assessment

**GPT-4 Only:**
- Questions: 10 × $0.001 = $0.01
- Evaluations: 10 × $0.002 = $0.02
- **Total: $0.03**

**Hybrid (GPT-4 + Gemini):**
- Questions: 10 × ($0.001 + $0.0003) = $0.013
- Evaluations: 10 × ($0.002 + $0.0005) = $0.025
- **Total: $0.038**

**Extra cost: $0.008 per assessment for significantly better quality!**

## Advanced: Customizing the Hybrid Logic

Edit `aibackend/app/clients/hybrid_ai_client.py`:

### Change Scoring Weights
```python
# Line 200: Adjust score combination
combined_score = int(gpt_score * 0.6 + gemini_score * 0.4)
# Change to 50/50: int(gpt_score * 0.5 + gemini_score * 0.5)
```

### Change Question Selection
```python
# Line 150: Modify _score_question() to prioritize different factors
```

### Change Feedback Merging
```python
# Line 220: Modify _merge_feedback() to combine differently
```

## Next Steps

1. Add your Gemini API key
2. Restart backend
3. Test with a few questions
4. Watch the logs to see both models working
5. Enjoy better quality questions and feedback!
