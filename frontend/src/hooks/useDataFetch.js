import { useState, useCallback, useRef } from 'react';

/**
 * Custom hook to handle API requests to the Python backend with caching.
 */
export const useDataFetch = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const cache = useRef(new Map());

  const fetchData = useCallback(async (topic, metadata = {}) => {
    // We construct a cache key based on the topic and serialized metadata
    const cacheKey = `${topic}_${JSON.stringify(metadata)}`;

    // Graceful fallback to cached values to handle network latency or repetitive clicks
    if (cache.current.has(cacheKey)) {
      setData(cache.current.get(cacheKey));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // The API proxy server (Vite or Nginx) must inject the Authorization header or session securely.
      // We do not hardcode secrets into the frontend build.
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: topic,
          skip_upload: metadata.skip_upload ?? true
        })
      });

      if (!response.ok) {
        throw new Error(`API returned status: ${response.status}`);
      }

      const result = await response.json();

      // Store the structured payload in cache and state
      cache.current.set(cacheKey, result);
      setData(result);

    } catch (err) {
      setError(err.message || 'An error occurred during data fetch');
      // If a request fails, we could also fall back to a previously cached value if we wanted to be extremely resilient,
      // but here we just expose the error.
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetchData };
};
