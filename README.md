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

4. Install the frontend dependencies and start the development servers in separate terminals:

   ```bash
   # Terminal 1 - Django API
   python manage.py runserver

   # Terminal 2 - React development server
   cd frontend
   npm install
   npm run dev
   ```

   The Vite dev server proxies API requests that start with `/mcp/` to the Django backend running on port 8000, so no additional
   CORS configuration is required. Update `frontend/.env.development` if your backend runs on a different host or port.

5. Visit `http://127.0.0.1:5173/` to use the MCP client interface during development.

   The MCP endpoint remains available at `http://127.0.0.1:8000/mcp/` and accepts JSON-RPC-style POST requests if you want to
   interact with it directly (for example via `curl` or Postman).

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

## Frontend configuration

The frontend reads runtime configuration from `.env` files using the `VITE_` prefix. Two presets are provided:

- `frontend/.env.development` &ndash; defaults the API base URL to `/mcp/` and proxies through `http://localhost:8000`.
- `frontend/.env.production` &ndash; defaults the API base URL to `/mcp/` when the React bundle is served by Django.

Override `VITE_API_BASE_URL` in these files (or create `.env.local`) to point at a different MCP host.

## Building for production

Create an optimised React build and copy it into Django's static directory:

```bash
cd frontend
npm run build:django
```

The compiled assets are stored in `mcp_server/static/frontend/`. Django automatically serves the bundled interface from the root
URL (`/`) when the build is present. If you prefer to deploy the frontend separately, run `npm run build` and host the contents of
`frontend/dist` on your static hosting provider of choice.

## Running tests

Execute the Django test runner:

```bash
python manage.py test
```

The unit tests exercise the MCP endpoint and ensure that OpenAI client calls are wired correctly via dependency injection and mocking.
