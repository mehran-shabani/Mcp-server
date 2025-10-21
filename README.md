# MCP Server

This repository contains a minimal Django project that exposes Machine Control Protocol (MCP)-style endpoints for experimenting with OpenAI integrations. The project uses an in-memory store to emulate database records and forwards prompts to the OpenAI Responses API using environment-driven configuration.

## Getting started

1. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure the required environment variables (see below).
3. Apply migrations and run the test suite to confirm the installation:

   ```bash
   python manage.py migrate
   python manage.py test
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

   The MCP endpoint is available at `http://127.0.0.1:8000/mcp/` and accepts JSON-RPC-style POST requests.

## Environment variables

The project reads the following environment variables in `mcp_server/settings.py`:

| Variable | Description | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | API key used to authenticate with OpenAI. | _Empty string (required for live requests)_ |
| `OPENAI_BASE_URL` | Base URL for the OpenAI API. Override when routing through compatible gateways. | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model identifier passed to the Responses API. | `gpt-4o-mini` |

At minimum you must provide `OPENAI_API_KEY` to generate real completions. The tests run without hitting the network by mocking the client.

## Fake data model

The `interactions` app seeds a handful of `InteractionRecord` entries that mimic database-backed resources. The MCP view exposes operations to list the available records, fetch an individual record, and generate OpenAI-backed responses using either the provided prompt or the record's default prompt.

## Running tests

Execute the Django test runner:

```bash
python manage.py test
```

The unit tests exercise the MCP endpoint and ensure that OpenAI client calls are wired correctly via dependency injection and mocking.
