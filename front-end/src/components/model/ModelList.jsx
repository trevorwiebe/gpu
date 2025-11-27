import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchModels } from '../../store'

import ModelItem from './ModelItem';
import Loader from '../small/Loader';
import Error from '../small/Error';

export default function ModelsList(){
  const dispatch = useDispatch();
  const { data: models, isLoading, error } = useSelector(state => state.models);

  useEffect(() =>{
    if(!models.length){
      dispatch(fetchModels())
    }
  }, [dispatch])

  if (isLoading) return <Loader/>
  if (error) return <Error text={error} />;

  return (
    <div>
      <ul>
        {models.map(model => (
          <li key={model._id}>
            <ModelItem name={model}/>
          </li>
        ))}
      </ul>
    </div>
  );
}