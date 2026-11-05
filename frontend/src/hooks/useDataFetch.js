import { useState, useCallback, useRef } from 'react';

/**
 * Custom hook to handle API requests to the Python backend with caching
 * and automatic 401 interception for dynamic token-refresh handshake.
 */
export const useDataFetch = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [authRequired, setAuthRequired] = useState(false);
  const cache = useRef(new Map());

  const fetchData = useCallback(async (topic, metadata = {}) => {
    const cacheKey = `${topic}_${JSON.stringify(metadata)}`;

    // Graceful fallback to cached values
    if (cache.current.has(cacheKey)) {
      setData(cache.current.get(cacheKey));
      return;
    }

    setLoading(true);
    setError(null);
    setAuthRequired(false);

    try {
      const headers = {
        'Content-Type': 'application/json'
      };

      // Forward custom basic credentials if provided in metadata
      if (metadata.customToken) {
        headers['Authorization'] = `Basic ${btoa(metadata.customToken)}`;
      }

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          topic: topic,
          skip_upload: metadata.skip_upload ?? true,
          canvas_format: metadata.canvas_format || ['landscape'],
          platforms: metadata.platforms || ['youtube']
        })
      });

      if (response.status === 401) {
        setAuthRequired(true);
        throw new Error('401 Unauthorized: Session credentials invalid or expired.');
      }

      if (!response.ok) {
        throw new Error(`API returned status: ${response.status}`);
      }

      const result = await response.json();
      cache.current.set(cacheKey, result);
      setData(result);
    } catch (err) {
      setError(err.message || 'An error occurred during data fetch');
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, authRequired, setAuthRequired, fetchData };
};
