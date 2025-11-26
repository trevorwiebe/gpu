import { useEffect } from 'react';
import { useAppDispatch, useAppSelector, fetchModels } from '../store'

export default function ModelsList(){
  const dispatch = useAppDispatch();
  const { data: models, isLoading, error } = useAppSelector(state => state.models);

  useEffect(() =>{
    dispatch(fetchModels())
  }, [dispatch])

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Models</h2>
      <ul>
        {models.map(model => (
          <li key={model.id}>
            {model.id} - {model.name}
          </li>
        ))}
      </ul>
    </div>
  );
}