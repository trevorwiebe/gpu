import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchModels } from '../store'

export default function ModelsList(){
  const dispatch = useDispatch();
  const { data: models, isLoading, error } = useSelector(state => state.models);

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