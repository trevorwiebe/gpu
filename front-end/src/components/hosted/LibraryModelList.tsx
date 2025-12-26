import { 
    useFetchLibraryQuery
} from '../../store';

import { useUser } from "@clerk/clerk-react";

interface LibraryModel {
    id: string,
    userId: string,
    modelId: string,
    modelName: String,
    health: boolean
}
export default function LibraryModelList(){

    const { user, isSignedIn } = useUser();

    const {
        data: library,
        error: libraryError,
        isLoading: libraryLoading
    } = useFetchLibraryQuery(user?.id, {skip: !user?.id});

    // if the user is not signed in, we don't want to show this
    if(!isSignedIn) return null

    var renderedContent;

    if (libraryLoading) {
        renderedContent = <div>Loading library...</div>
    } else if (libraryError) {
        renderedContent = <div className="text-red-500">Error loading library</div>
    } else if (!library || library.length === 0) {
        renderedContent = <div>No models in library</div>
    } else {
        renderedContent = library.map((model: LibraryModel) => {
            return (
                <div key={model.id} className="bg-gray-200 my-2 p-4 rounded-full">
                    <p>{model.modelName}</p>
                    <p className='text-gray-500 text-xs'>ModelId: {model.modelId}</p>
                </div>
            );
        });
    }

    return (
        <div className="my-4 p-4">
            <h2 className="text-xl font-bold mb-4">My Library Models</h2>
            {renderedContent}
        </div>
    )
}