# OpenAI ChatGPT-5 Setup

## Environment Configuration

Add these variables to your `.env` file:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5  # Will fallback to gpt-4o if GPT-5 not available
```

## Model Selection

The system is configured to use **ChatGPT-5** by default with automatic fallback:

1. **Primary Model**: `gpt-5` (when available)
2. **Fallback Model**: `gpt-4o` (if GPT-5 not found)

## Automatic Fallback Logic

- The system first attempts to use GPT-5
- If GPT-5 returns a "model not found" error, it automatically falls back to GPT-4o
- Pricing is automatically adjusted based on the model used
- All logging and UI will reflect the actual model being used

## Pricing

- **GPT-5** (estimated): $0.01 input / $0.03 output per 1K tokens
- **GPT-4o** (current): $0.005 input / $0.015 output per 1K tokens

## Manual Model Override

You can force a specific model by setting:

```bash
OPENAI_MODEL=gpt-4o  # Force GPT-4o
OPENAI_MODEL=gpt-5   # Force GPT-5 (default)
```

## Status

- ✅ **UI**: Shows "ChatGPT-5" branding
- ✅ **API**: Configured for GPT-5 with GPT-4o fallback
- ✅ **Pricing**: Dynamic pricing based on actual model used
- ✅ **Logging**: Shows actual model being used
- ✅ **Error Handling**: Graceful fallback if GPT-5 unavailable

The system is **future-ready** for ChatGPT-5 and will automatically use it once OpenAI releases it!
