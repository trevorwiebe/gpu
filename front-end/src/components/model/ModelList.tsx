import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useUser } from "@clerk/clerk-react";

import { AppDispatch } from '../../store'
import { fetchModels } from '../../store'
import { RootState } from '../../types'

import ModelItem from './ModelItem';
import Loader from '../small/Loader';
import Error from '../small/Error';

export default function ModelsList() {
  const dispatch = useDispatch<AppDispatch>();
  const { data: models, isLoading, error } = useSelector((state: RootState) => state.models);

  const { isSignedIn } = useUser();

  useEffect(() =>{
    if(!models.length){
      dispatch(fetchModels())
    }
  }, [dispatch, models.length])

  if (isLoading) return <Loader/>
  if (error) return <Error text={error} />;

  return (
    <div>
      <ul>
        {models.map(model => (
          <li key={model.id}>
            <ModelItem name={model} authenticated={isSignedIn}/>
          </li>
        ))}
      </ul>
    </div>
  );
}