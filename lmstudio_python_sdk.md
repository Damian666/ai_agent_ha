# LM Studio Python SDK Documentation

**Source:** [https://lmstudio.ai/docs/python](https://lmstudio.ai/docs/python)

## Table of Contents

1.  [Getting Started](#getting-started)
2.  [Chat Completions](#chat-completions)
3.  [Text Completions](#text-completions)
4.  [Managing Models (Loading/Unloading)](#managing-models-loadingunloading)
5.  [Parameters & Configuration](#parameters--configuration)

---

## Getting Started

### Installing the SDK

`lmstudio-python` is available as a PyPI package.

```bash
pip install lmstudio
```

### Quick Example: Chat with a Llama Model

```python
import lmstudio as lms 

model = lms.llm("qwen/qwen3-4b-2507") 
result = model.respond("What is the meaning of life?") 
print(result)
```

### Getting Local Models

The above code requires the `qwen3-4b-2507` model. If you don't have the model, run:

```bash
lms get qwen/qwen3-4b-2507
```

### API Flavors

1.  **Interactive convenience API**: `model = lms.llm()` - for scripts and notebooks.
2.  **Synchronous scoped resource API**: Uses context managers for deterministic resource cleanup.
3.  **Asynchronous structured concurrency API**: For async apps using libraries like `asyncio` or `trio`.

---

## Chat Completions

**Full Docs:** [https://lmstudio.ai/docs/python/llm-prediction/chat-completion](https://lmstudio.ai/docs/python/llm-prediction/chat-completion)

### Quick Example

```python
import lmstudio as lms 
model = lms.llm() 
print(model.respond("What is the meaning of life?"))
```

### Streaming a Response

```python
import lmstudio as lms 
model = lms.llm() 
for fragment in model.respond_stream("What is the meaning of life?"): 
    print(fragment.content, end="", flush=True) 
print() 
```

### Multi-turn Chat / Managing Context

```python
import lmstudio as lms 

# Create a chat with an initial system prompt
chat = lms.Chat("You are a resident AI philosopher.") 

# Add user message
chat.add_user_message("What is the meaning of life?") 

# Generate response
result = model.respond(chat)
print(result)
```

### Print Prediction Stats

```python
print("Model used:", result.model_info.display_name) 
print("Predicted tokens:", result.stats.predicted_tokens_count) 
print("Time to first token (seconds):", result.stats.time_to_first_token_sec) 
print("Stop reason:", result.stats.stop_reason)
```

---

## Text Completions

**Full Docs:** [https://lmstudio.ai/docs/python/llm-prediction/completion](https://lmstudio.ai/docs/python/llm-prediction/completion)

### Generate a Completion

```python
# 'complete' is used for raw text completion (not chat)
result = model.complete("My name is", config={"maxTokens": 100}) 
print(result)
```

### Streaming Completion

```python
prediction_stream = model.complete_stream(
    "Once upon a time", 
    config={"stopStrings": ["\n"]} 
) 
for fragment in prediction_stream: 
    print(fragment.content, end="", flush=True)
```

---

## Managing Models (Loading/Unloading)

**Full Docs:** [https://lmstudio.ai/docs/python/manage-models/loading](https://lmstudio.ai/docs/python/manage-models/loading)

### Get Current Model

```python
# Uses the model currently loaded in LM Studio or loads one if specified
model = lms.llm()
```

### Load Specific Model

```python
# Loads 'qwen/qwen3-4b-2507' if not loaded, or returns it if it is
model = lms.llm("qwen/qwen3-4b-2507")
```

### Load New Instance

Allows loading multiple instances of the same model.

```python
client = lms.get_default_client() 
model1 = client.llm.load_new_instance("qwen/qwen3-4b-2507") 
model2 = client.llm.load_new_instance("qwen/qwen3-4b-2507", "my-second-model")
```

### Unload Model

```python
model.unload()
```

### Set Auto Unload Timer (TTL)

```python
# Model will stay loaded for 3600 seconds of idle time
model = lms.llm("qwen/qwen3-4b-2507", ttl=3600)
```

---

## Parameters & Configuration

**Full Docs:** [https://lmstudio.ai/docs/python/llm-prediction/parameters](https://lmstudio.ai/docs/python/llm-prediction/parameters)

### Inference Parameters (per request)

Start `respond` or `complete` with a `config` dictionary.

```python
result = model.respond(chat, config={ 
    "temperature": 0.6, 
    "maxTokens": 50, 
    "topP": 0.9
})
```

**Common Parameters:**
- `temperature`: Controls randomness (higher = more random).
- `maxTokens`: Limit generated tokens.
- `topP`: Nucleus sampling.

### Load Parameters (when loading model)

Set these when initializing `lms.llm()` or `load_new_instance()`.

```python
model = lms.llm("qwen2.5-7b-instruct", config={ 
    "contextLength": 8192, 
    "gpu": { 
        "ratio": 0.5, # Offload 50% of layers to GPU
    } 
})
```

**Common Load Parameters:**
- `contextLength`: Max context window size.
- `gpu.ratio`: 0.0 to 1.0 (portion of model to offload to GPU).

---
