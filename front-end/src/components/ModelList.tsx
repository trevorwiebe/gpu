import React, { useState, useEffect, useCallback, useRef } from 'react';

interface Model {
  id: string;
  tags: string[];
  downloads: number;
}

const useInfiniteModels = () => {
  
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [offset, setOffset] = useState<number>(0);
  const loadingRef = useRef<boolean>(false);

  const fetchModels = useCallback(async () => {
    if (loadingRef.current || !hasMore) return;
    
    loadingRef.current = true;
    setLoading(true);
    
    try {
      const url = `https://huggingface.co/api/models?filter=text-generation&sort=downloads&direction=-1&limit=100&offset=${offset}&full=true`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: Model[] = await response.json();
      
      if (data.length === 0) {
        setHasMore(false);
      } else {
        setModels(prev => [...prev, ...data]);
        setOffset(prev => prev + data.length);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  }, [offset, hasMore]);

  useEffect(() => {
    fetchModels();
  }, []);

  return { models, loading, error, hasMore, fetchMore: fetchModels };
};

const ModelList: React.FC = () => {
  const { models, loading, error, hasMore, fetchMore } = useInfiniteModels();
  const observer = useRef<IntersectionObserver | null>(null);
  const lastModelRef = useRef<HTMLLIElement>(null);

  useEffect(() => {
    if (loading) return;
    
    observer.current = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore) {
          fetchMore();
        }
      },
      { threshold: 0.1 }
    );

    if (lastModelRef.current) {
      observer.current.observe(lastModelRef.current);
    }

    return () => {
      if (observer.current && lastModelRef.current) {
        observer.current.unobserve(lastModelRef.current);
      }
    };
  }, [loading, hasMore, fetchMore]);

  if (error) return <div className="text-red-500 p-4">Error: {error}</div>;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Text Generation Models</h2>
      <ul className="space-y-2">
        {models.map((model, index) => (
          <li 
            key={model.id} 
            ref={index === models.length - 1 ? lastModelRef : null}
            className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="font-medium text-gray-900">{model.id}</div>
            <div className="text-sm text-gray-600">Downloads: {model.downloads.toLocaleString()}</div>
          </li>
        ))}
      </ul>
      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      )}
      {!hasMore && models.length > 0 && (
        <div className="text-center py-4 text-gray-500">
          No more models to load
        </div>
      )}
    </div>
  );
};

export default ModelList;