import {
    useFetchLibraryQuery,
    useFetchNodesQuery,
    useAssignModelToNodeMutation
} from '../../store';

import { useUser } from "@clerk/clerk-react";
import AssignModel from './AssignModel';
import AssignedNodeChips from './AssignedNodeChips';

import { LibraryModel } from '../../types'

export default function LibraryModelList(){

    const { user, isSignedIn } = useUser();

    const {
        data: library,
        error: libraryError,
        isLoading: libraryLoading
    } = useFetchLibraryQuery(user?.id, {skip: !user?.id});

    const {
        data: nodes,
        error: nodesError,
        isLoading: nodesLoading
    } = useFetchNodesQuery(user?.id, {skip: !user?.id});

    const [assignModelToNode] = useAssignModelToNodeMutation();

    // if the user is not signed in, we don't want to show this
    if(!isSignedIn) return null

    const createNodeSelectHandler = (modelId: string) => async (nodeId: string) => {
        if (!user?.id) return;

        try {
            await assignModelToNode({
                userId: user.id,
                nodeId,
                modelId
            }).unwrap();
        } catch (error) {
            console.error('Failed to assign model:', error);
        }
    };

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
                <div key={model.modelId} className="bg-gray-200 my-2 p-4 rounded-[3vw]">
                    <div className="flex justify-between items-start">
                        <div>
                            <p>{model.modelName}</p>
                            <p className='text-gray-500 text-xs'>Model Id: {model.modelId}</p>
                            <p className='text-gray-500 text-xs'>Hugging Face Model Id: {model.huggingFaceModelId}</p>
                            <AssignedNodeChips
                                modelId={model.modelId}
                                nodes={nodes || []}
                            />
                        </div>
                        <AssignModel
                            modelId={model.modelId}
                            nodes={nodes || []}
                            onNodeSelected={createNodeSelectHandler(model.modelId)}
                        />
                    </div>
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