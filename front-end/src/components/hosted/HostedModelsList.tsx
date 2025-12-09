import { 
  useFetchModelsQuery, 
  useFetchLibraryQuery,
} from '../../store';

import { useUser } from "@clerk/clerk-react";

interface LibraryModel {
    id: string,
    userId: string,
    modelId: string,
    health: boolean
}
export default function HostedModelsList(){

    const { user, isSignedIn } = useUser();

    // if the user is not signed in, we don't want to show this
    if(!isSignedIn) return

    const {
        data: library,
        error: libraryError,
        isLoading: libraryLoading
    } = useFetchLibraryQuery(user?.id, {skip: !user?.id});

    if (libraryLoading) return <div className="m-4 p-4">Loading library...</div>
    if (libraryError) return <div className="m-4 p-4 text-red-500">Error loading library</div>
    if (!library || library.length === 0) return <div className="m-4 p-4">No models in library</div>

    const renderedLibrary = library.map((model: LibraryModel) => {
        return (
            <div key={model.id} className="bg-gray-200 my-2 p-2 rounded-full">
                {model.modelId}
            </div>
        );
    });

    return (
        <div className="my-4 p-4">
            <h2 className="text-xl font-bold mb-4">My Hosted Models</h2>
            {renderedLibrary}
        </div>
    )
}