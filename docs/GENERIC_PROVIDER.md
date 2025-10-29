# Generic Provider Guide

## Overview

The **generic provider** is a universal client that works with **any OpenAI-compatible API endpoint**. Use it when you want to:

- Try new AI services without writing code
- Use multiple models from the same service
- Connect to custom or self-hosted endpoints
- Avoid creating dedicated provider clients

## When to Use

✅ **Use generic provider when:**
- Service has OpenAI-compatible API format
- You want to test a new service quickly
- You need multiple models from one service
- You have a custom/self-hosted endpoint
- Service isn't in the built-in providers list

⚠️ **Use dedicated provider when:**
- Service has a specialized SDK (better error handling)
- You need service-specific features
- Service is widely used (better support)

## Quick Start

### 1. Basic Configuration

```yaml
# providers.yaml
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer your-api-key-here
```

### 2. Run

```bash
./index.py --provider generic --days 7
```

### 3. Environment Variables (Alternative)

Instead of hardcoding in YAML:

```bash
# .env
GENERIC_API_KEY=your-api-key
GENERIC_API_URL=https://openrouter.ai/api/v1
```

```yaml
# providers.yaml
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    # Automatically uses GENERIC_API_KEY and GENERIC_API_URL
```

## Supported Services

The generic provider works with any service implementing the OpenAI chat completions format:

### OpenRouter (100+ Models)

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://your-site.com  # Optional
    X-Title: Drupal Weekly  # Optional
```

**Popular OpenRouter models:**
- `meta-llama/llama-3.1-70b-instruct`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`
- `openai/gpt-4`
- `mistralai/mixtral-8x7b-instruct`

### Together AI

```yaml
together:
  client: generic_client
  model: mistralai/Mixtral-8x7B-Instruct-v0.1
  temperature: 0.2
  api_url: https://api.together.xyz/v1
  headers:
    Authorization: Bearer ${TOGETHER_API_KEY}
```

### Groq (Fast Inference)

```yaml
groq:
  client: generic_client
  model: llama-3.1-70b-versatile
  temperature: 0.2
  api_url: https://api.groq.com/openai/v1
  headers:
    Authorization: Bearer ${GROQ_API_KEY}
```

**Available Groq models:**
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

### Perplexity (Online Models)

```yaml
perplexity:
  client: generic_client
  model: llama-3.1-sonar-large-128k-online
  temperature: 0.2
  api_url: https://api.perplexity.ai
  headers:
    Authorization: Bearer ${PERPLEXITY_API_KEY}
```

### Fireworks AI

```yaml
fireworks:
  client: generic_client
  model: accounts/fireworks/models/llama-v3p1-70b-instruct
  temperature: 0.2
  api_url: https://api.fireworks.ai/inference/v1
  headers:
    Authorization: Bearer ${FIREWORKS_API_KEY}
```

### Azure OpenAI

```yaml
azure:
  client: generic_client
  model: gpt-4  # Your deployment name
  temperature: 0.2
  api_url: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
  headers:
    api-key: ${AZURE_OPENAI_API_KEY}
```

### LiteLLM Proxy

```yaml
litellm:
  client: generic_client
  model: gpt-4  # Model from litellm_config.yaml
  temperature: 0.2
  api_url: http://localhost:4000
```

### Custom Self-Hosted

```yaml
custom:
  client: generic_client
  model: your-model-name
  temperature: 0.2
  api_url: https://your-endpoint.com/v1
  headers:
    Authorization: Bearer your-token
```

## Advanced Configurations

### Multiple Models from Same Service

```yaml
providers:
  llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  claude-sonnet:
    client: generic_client
    model: anthropic/claude-3.5-sonnet
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  gemini-pro:
    client: generic_client
    model: google/gemini-pro-1.5
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}
```

Then use:
```bash
./index.py --provider llama-70b --days 7
./index.py --provider claude-sonnet --days 7
./index.py --provider gemini-pro --days 7
```

### With Custom Headers

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://drupal-weekly.example.com
    X-Title: Drupal Weekly Aggregator
    X-Custom-Header: custom-value
```

### With Environment Variables

```bash
# .env
GENERIC_API_KEY=sk-or-v1-xxx
GENERIC_API_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=sk-or-v1-xxx
TOGETHER_API_KEY=xxx
GROQ_API_KEY=gsk_xxx
```

```yaml
# providers.yaml - uses environment variables
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    # api_url from GENERIC_API_URL
    # Authorization from GENERIC_API_KEY

  together:
    client: generic_client
    model: mistralai/Mixtral-8x7B-Instruct-v0.1
    temperature: 0.2
    api_url: https://api.together.xyz/v1
    headers:
      Authorization: Bearer ${TOGETHER_API_KEY}
```

## Testing

### Test with Cached Sources

```bash
# Fetch data once
./index.py --fetch-only

# Test different models without re-fetching
./index.py --provider generic --use-sources 2025-10-25 --email no
./index.py --provider llama-70b --use-sources 2025-10-25 --email no
./index.py --provider claude-sonnet --use-sources 2025-10-25 --email no
```

### Compare Model Outputs

```bash
# Generate summaries with different models
DATE=$(date +%Y-%m-%d)

./index.py --provider llama-70b --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_llama70b.md

./index.py --provider claude-sonnet --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_claude.md

./index.py --provider gemini-pro --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_gemini.md

# Compare outputs
diff runs/$DATE/summary_llama70b.md runs/$DATE/summary_claude.md
```

## Troubleshooting

### Error: "API URL required"

```
ValueError: API URL required. Provide via api_url parameter or GENERIC_API_URL environment variable.
```

**Solution:** Set `api_url` in providers.yaml or `GENERIC_API_URL` in .env:

```yaml
generic:
  api_url: https://openrouter.ai/api/v1  # Add this
```

### Error: HTTP 401 Unauthorized

```
RuntimeError: Generic API HTTP error: 401
```

**Solution:** Check your API key:
1. Verify key is correct in .env or providers.yaml
2. Check Authorization header format
3. Ensure key has proper permissions

```yaml
headers:
  Authorization: Bearer your-api-key  # Check format
```

### Error: HTTP 404 Not Found

```
RuntimeError: Generic API HTTP error: 404
```

**Solution:** Check API URL and model name:
1. Verify URL ends with `/v1` or correct version
2. Check model name is valid for that service
3. Some services require full paths (e.g., Azure)

### Error: Model not found

```
RuntimeError: Generic API error: model not available
```

**Solution:** Verify model name for your service:
- **OpenRouter:** Use format `provider/model-name`
- **Groq:** Use exact model ID from their docs
- **LiteLLM:** Use `model_name` from litellm_config.yaml

### Slow Response

If API is slow:

```yaml
generic:
  client: generic_client
  model: your-model
  temperature: 0.2
  api_url: https://your-service.com/v1
  # Consider faster models or services
```

**Tips:**
- Groq is very fast (optimized inference)
- Smaller models respond faster
- Use dedicated providers for better performance

## Best Practices

### 1. Use Environment Variables for Keys

```yaml
# Good
headers:
  Authorization: Bearer ${OPENROUTER_API_KEY}

# Bad (security risk)
headers:
  Authorization: Bearer sk-or-hardcoded-key
```

### 2. Name Providers Descriptively

```yaml
# Good
providers:
  openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

# Less clear
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
```

### 3. Document Custom Endpoints

```yaml
# Custom endpoint with documentation
custom-endpoint:
  client: generic_client
  model: custom-model-v2
  temperature: 0.2
  api_url: https://internal.company.com/ai/v1
  # Note: Internal AI gateway, uses corporate auth
  headers:
    Authorization: Bearer ${COMPANY_AI_TOKEN}
```

### 4. Test Before Production

```bash
# Always test new configurations with cached sources
./index.py --provider new-provider --use-sources latest --email no
```

## Examples

See `providers.generic.example.yaml` for complete working examples of:
- OpenRouter (multiple models)
- Together AI
- Groq
- Perplexity
- Fireworks AI
- Azure OpenAI
- LiteLLM
- Custom endpoints

## See Also

- [Custom API URLs Guide](CUSTOM_API_URLS.md) - Proxy configuration
- [Proxy Quick Start](PROXY_QUICKSTART.md) - LiteLLM and Portkey setup
- [Usage Guide](../USAGE.md) - Basic usage patterns
- `providers.generic.example.yaml` - Ready-to-use configurations
