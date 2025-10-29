# Custom API URLs and Proxy Configuration

This document explains how to use custom API endpoints and proxy services (like Portkey) with the Drupal News Aggregator.

## Overview

You can configure custom API URLs and headers for any provider in `providers.yaml`. This is useful for:

- Using proxy services (Portkey, LiteLLM, etc.)
- Custom deployments
- Load balancers
- Local development endpoints
- Rate limiting management
- Cost tracking and monitoring

## Configuration

Add `api_url` and optionally `headers` to any provider in `providers.yaml`:

```yaml
providers:
  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://your-custom-url.com/v1
    headers:
      Custom-Header: value
      Another-Header: another-value
```

## Example: Portkey Proxy

[Portkey](https://portkey.ai) provides AI gateway features like caching, fallbacks, and monitoring.

### Step 1: Get Portkey Keys

1. Sign up at https://portkey.ai
2. Create an API key
3. Create a virtual key for Grok (or your provider)

### Step 2: Configure providers.yaml

```yaml
providers:
  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://api.portkey.ai/v1
    headers:
      x-portkey-api-key: pk-***YOUR_PORTKEY_API_KEY***
      x-portkey-virtual-key: vk-***YOUR_GROK_VIRTUAL_KEY***
```

### Step 3: Keep your provider API key

Still set `GROK_API_KEY` in `.env` - Portkey will use it via the virtual key:

```bash
GROK_API_KEY=xai-***YOUR_GROK_API_KEY***
```

### Step 4: Run normally

```bash
./index.py --provider grok --days 7
```

## Advanced Portkey Features

### Request Tracing

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-virtual-key: vk-***
    x-portkey-trace-id: drupal-news-{date}
    x-portkey-metadata: '{"source":"drupal-aggregator"}'
```

### Cache Control

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-virtual-key: vk-***
    x-portkey-cache-force-refresh: "true"
```

### Fallback Configuration

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-config: config-id-with-fallbacks
```

## Other Proxy Services

### LiteLLM Proxy

[LiteLLM](https://docs.litellm.ai) is a unified interface to 100+ LLMs with built-in load balancing, fallbacks, and cost tracking.

#### Setup LiteLLM Proxy Server

```bash
# Install LiteLLM
pip install litellm[proxy]

# Start proxy server
litellm --config litellm_config.yaml
```

Example `litellm_config.yaml`:
```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: grok-beta
    litellm_params:
      model: xai/grok-beta
      api_key: os.environ/GROK_API_KEY
```

#### Configure Drupal Aggregator with LiteLLM

```yaml
# providers.yaml - Use LiteLLM for all providers
providers:
  openai:
    client: openai_client
    model: gpt-4  # Model name from litellm_config.yaml
    temperature: 0.2
    api_url: http://localhost:4000  # LiteLLM default port

  anthropic:
    client: openai_client  # LiteLLM is OpenAI-compatible
    model: claude-3-5-sonnet
    temperature: 0.2
    api_url: http://localhost:4000

  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: http://localhost:4000
```

#### Advanced LiteLLM Features

**Load Balancing:**
```yaml
# In LiteLLM config
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_1

  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_2  # Automatic rotation
```

**Cost Tracking with Custom Headers:**
```yaml
# providers.yaml
openai:
  api_url: http://localhost:4000
  headers:
    user: drupal-aggregator
    tags: news-report
```

**LiteLLM with Authentication:**
```yaml
# If LiteLLM proxy has auth enabled
openai:
  api_url: http://localhost:4000
  headers:
    Authorization: Bearer your-litellm-master-key
```

### OpenRouter (Already a Proxy)

```yaml
openrouter:
  client: openrouter_client
  model: meta-llama/llama-3.1-8b-instruct
  # Uses OpenRouter's built-in routing
```

### Custom OpenAI-Compatible Endpoints

Any provider using OpenAI-compatible format:

```yaml
custom_provider:
  client: grok_client  # Reuse any OpenAI-compatible client
  model: your-model-name
  api_url: https://your-endpoint.com/v1
  headers:
    Authorization: Bearer your-token
```

## Local Endpoints

### Ollama (Custom Port)

```yaml
ollama:
  client: ollama_client
  model: qwen2.5:7b-instruct
  api_url: http://192.168.1.100:11434
```

### LM Studio (Custom Port)

```yaml
lmstudio:
  client: lmstudio_client
  model: your-model
  api_url: http://localhost:1234
```

## Environment Variables

You can use environment variables in headers:

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: ${PORTKEY_API_KEY}
    x-portkey-virtual-key: ${PORTKEY_GROK_KEY}
```

Then in `.env`:
```bash
PORTKEY_API_KEY=pk-***
PORTKEY_GROK_KEY=vk-***
```

## Supported Providers

Custom URLs and headers work with:
- ✅ **grok** - Full support
- ✅ **openai** - Via custom endpoint
- ✅ **anthropic** - Via proxy
- ✅ **ollama** - Custom host/port
- ✅ **openrouter** - Via Portkey
- ⚠️ **gemini** - Limited (uses official SDK)

## Testing

Test your configuration:

```bash
# Dry run to verify config loads
./index.py --provider grok --dry-run

# Fetch-only (no API calls)
./index.py --fetch-only

# Full run with custom endpoint
./index.py --provider grok --use-sources 2025-10-25 --email no
```

## Troubleshooting

### Headers not working

Check that your provider client supports custom headers. Currently supported:
- `grok_client.py` ✅
- Other clients may need updates

### Authentication errors

1. Verify your API keys in `.env`
2. Check Portkey virtual key is correct
3. Ensure headers are formatted correctly

### Timeout issues

Increase timeout if using slow proxies:

```python
# In provider client:
timeout=300.0  # 5 minutes
```

## Security Notes

- Never commit API keys to git
- Use `.env` for secrets
- Consider using environment variables for Portkey keys
- Rotate keys regularly
- Monitor usage through Portkey dashboard

## Generic Provider (New!)

For maximum flexibility, use the **generic provider** which works with ANY OpenAI-compatible API:

```yaml
# providers.yaml
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer your-api-key
```

Works with: OpenRouter, Together AI, Groq, Perplexity, Fireworks AI, Azure OpenAI, custom endpoints, and more.

**See:** [Generic Provider Guide](GENERIC_PROVIDER.md) for complete documentation.

## Quick Start Examples

The repository includes ready-to-use configuration examples:

- `providers.generic.example.yaml` - Generic provider for any service (NEW!)
- `providers.portkey.example.yaml` - Portkey proxy configuration
- `providers.litellm.example.yaml` - LiteLLM proxy configuration
- `litellm_config.example.yaml` - LiteLLM server configuration

Copy and customize these files for your setup:

```bash
# For LiteLLM
cp litellm_config.example.yaml litellm_config.yaml
cp providers.litellm.example.yaml providers.yaml
litellm --config litellm_config.yaml

# For Portkey
cp providers.portkey.example.yaml providers.yaml
# Edit providers.yaml with your Portkey keys
```

## Comparison: Portkey vs LiteLLM

| Feature | Portkey | LiteLLM |
|---------|---------|---------|
| **Hosting** | Cloud (SaaS) | Self-hosted |
| **Setup** | API keys only | Requires local server |
| **UI Dashboard** | ✅ Full web UI | ⚠️ Limited |
| **Cost** | Paid (free tier) | Free (open source) |
| **Load Balancing** | ✅ Yes | ✅ Yes |
| **Fallbacks** | ✅ Yes | ✅ Yes |
| **Caching** | ✅ Yes | ✅ Yes (Redis) |
| **Analytics** | ✅ Built-in | ⚠️ Via integrations |
| **Rate Limiting** | ✅ Yes | ✅ Yes (Redis) |
| **Best For** | Quick setup, monitoring | Full control, privacy |

## See Also

- [Portkey Documentation](https://docs.portkey.ai)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [LiteLLM Documentation](https://docs.litellm.ai)
