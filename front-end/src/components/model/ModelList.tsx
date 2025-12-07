import { useMemo } from 'react';
import { useUser } from "@clerk/clerk-react";
import { 
  useFetchModelsQuery, 
  useFetchLibraryQuery,
  useAddToLibraryMutation,
  useRemoveFromLibraryMutation
 } from '../../store';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

import { Model, Library } from '../../types'

import ModelItem from './ModelItem';
import Loader from '../small/Loader';
import Error from '../small/Error';

export default function ModelsList() {

  const { user, isSignedIn } = useUser();

  const { 
    data: models = [], 
    error: modelError,
    isLoading: modelLoading
  } = useFetchModelsQuery();

  const { 
    data: library, 
    error: libraryError, 
    isLoading: libraryLoading 
  } = useFetchLibraryQuery(user?.id);

  const [addToLibrary] = useAddToLibraryMutation();
  const [removeFromLibrary] = useRemoveFromLibraryMutation()

  const { sortBy, sortOrder } = useSelector((state: RootState) => state.modelsSort);
  
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

  if (modelLoading) return <Loader/>
  if (modelError) return <Error text={"Something went wrong"} />;

  const inLibrary = (model: Model, library?: Library[]) => {
    return library?.some(item => item.modelId === model._id) || false
  }

  const setInLibrary = async (model: Model, favorite: Boolean) => {

    const userId = user?.id;
    const modelId = model._id;

    if(favorite){
      await addToLibrary({userId, modelId});
    }else{
      const libraryEntry = library.find((item: Library) => item.modelId === model._id);
      await removeFromLibrary(libraryEntry.id);
    }
  }

  return (
    <div>
      <ul>
        {sortedModels?.map(model => (
          <li key={model.id}>
            <ModelItem 
              model={model}
              authenticated={isSignedIn}
              inLibrary={inLibrary(model, library)}
              onFavorite={setInLibrary}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}