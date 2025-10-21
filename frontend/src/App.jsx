import { useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';

const normaliseBaseUrl = (value) => {
  if (!value) {
    return '/mcp/';
  }
  return value.endsWith('/') ? value : `${value}/`;
};

const buildJsonRpcPayload = (method, params = {}) => ({
  jsonrpc: '2.0',
  id: Date.now(),
  method,
  params,
});

function App() {
  const apiBaseUrl = useMemo(() => normaliseBaseUrl(import.meta.env.VITE_API_BASE_URL), []);
  const [resources, setResources] = useState([]);
  const [selectedRecordId, setSelectedRecordId] = useState('');
  const [prompt, setPrompt] = useState('');
  const [responseData, setResponseData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isListing, setIsListing] = useState(false);

  const performRequest = useCallback(
    async (payload) => {
      const response = await fetch(apiBaseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return response.json();
    },
    [apiBaseUrl]
  );

  useEffect(() => {
    const loadResources = async () => {
      setIsListing(true);
      setError('');
      try {
        const payload = buildJsonRpcPayload('interactions.list');
        const data = await performRequest(payload);
        const availableResources = data?.result?.resources || [];
        setResources(availableResources);
        if (availableResources.length > 0) {
          const [first] = availableResources;
          setSelectedRecordId(String(first.id));
          if (first.sample_prompt) {
            setPrompt((current) => current || first.sample_prompt || '');
          }
        }
      } catch (err) {
        setError(`Failed to load interactions: ${err.message}`);
      } finally {
        setIsListing(false);
      }
    };

    loadResources();
  }, [performRequest]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedRecordId) {
      setError('Please choose an interaction to run.');
      return;
    }

    setIsLoading(true);
    setError('');
    setResponseData(null);

    try {
      const params = { record_id: Number(selectedRecordId) };
      if (prompt.trim()) {
        params.prompt = prompt.trim();
      }

      const payload = buildJsonRpcPayload('interactions.generate', params);
      const data = await performRequest(payload);

      if (data.error) {
        setError(data.error?.message || 'The MCP request returned an error.');
      } else {
        setResponseData(data.result);
      }
    } catch (err) {
      setError(`Request failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app__header">
        <h1>MCP Client</h1>
        <p className="app__subtitle">
          API base URL: <code>{apiBaseUrl}</code>
        </p>
      </header>
      <main className="app__layout">
        <section className="panel">
          <h2 className="panel__title">Prompt</h2>
          <form className="prompt-form" onSubmit={handleSubmit}>
            <label className="prompt-form__field">
              <span>Interaction</span>
              <select
                value={selectedRecordId}
                onChange={(event) => setSelectedRecordId(event.target.value)}
                disabled={isListing || resources.length === 0}
              >
                {resources.length === 0 ? (
                  <option value="">No interactions available</option>
                ) : (
                  resources.map((resource) => (
                    <option key={resource.id} value={resource.id}>
                      {resource.name || `Interaction ${resource.id}`}
                    </option>
                  ))
                )}
              </select>
            </label>
            <label className="prompt-form__field">
              <span>Prompt</span>
              <textarea
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                rows={6}
                placeholder="Enter a prompt to send to the MCP backend"
              />
            </label>
            <button className="prompt-form__submit" type="submit" disabled={isLoading || isListing}>
              {isLoading ? 'Submitting…' : 'Submit'}
            </button>
          </form>
          {error && <p className="status status--error">{error}</p>}
          {!error && isListing && <p className="status">Loading interactions…</p>}
        </section>
        <section className="panel">
          <h2 className="panel__title">MCP Response</h2>
          {responseData ? (
            <pre className="response-viewer">{JSON.stringify(responseData, null, 2)}</pre>
          ) : (
            <p className="placeholder">
              {isLoading
                ? 'Awaiting response from the server…'
                : 'Submit a prompt to view the MCP response.'}
            </p>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
