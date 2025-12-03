import { useMemo } from 'react';
import { useUser } from "@clerk/clerk-react";
import { useFetchModelsQuery } from '../../store';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

import ModelItem from './ModelItem';
import Loader from '../small/Loader';
import Error from '../small/Error';

export default function ModelsList() {

  const { data: models = [], error, isLoading} = useFetchModelsQuery();
  const { sortBy, sortOrder } = useSelector((state: RootState) => state.modelsSort);
  const { isSignedIn } = useUser();

  console.log(models);

  const sortedModels = useMemo(() => {
    const sorted = [...models].sort((a, b) => {
      let valueA = a[sortBy as keyof typeof a];
      let valueB = b[sortBy as keyof typeof b];
      
      // Handle dates
      if (sortBy === 'createdAt') {
        valueA = new Date(valueA as string).getTime();
        valueB = new Date(valueB as string).getTime();
      }
      
      // Handle strings
      if (typeof valueA === 'string' && typeof valueB === 'string') {
        return sortOrder === 'asc' 
          ? valueA.localeCompare(valueB)
          : valueB.localeCompare(valueA);
      }
      
      // Handle numbers
      if (sortOrder === 'asc') {
        return (valueA as number) - (valueB as number);
      } else {
        return (valueB as number) - (valueA as number);
      }
    });
    
    return sorted;
  }, [models, sortBy, sortOrder]);

  if (isLoading) return <Loader/>
  if (error) return <Error text={"Something went wrong"} />;

  return (
    <div>
      <ul>
        {sortedModels?.map(model => (
          <li key={model.id}>
            <ModelItem name={model} authenticated={isSignedIn}/>
          </li>
        ))}
      </ul>
    </div>
  );
}