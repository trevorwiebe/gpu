import { 
    useFetchNodesQuery
} from '../../store';

import { useUser } from "@clerk/clerk-react";
import { NodeModel } from "@/types"

export default function NodeList(){

    const { user, isSignedIn } = useUser();

    const {
        data: nodeData,
        error: nodeError,
        isLoading: nodesLoading
    } = useFetchNodesQuery(user?.id, {skip: !user?.id});

    if(!isSignedIn) return null

    var renderedContent

    if (nodesLoading) {
        renderedContent = <div>Loading nodes...</div>
    } else if (nodeError) {
        renderedContent = <div className="text-red-500">Error loading nodes</div>
    } else if (!nodeData || nodeData.length === 0) {
        renderedContent = <div>No authenticated nodes</div>
    } else {
        renderedContent = nodeData.map((node: NodeModel) => {
            return (
                <div key={node.nodeId} className="my-2 p-4 bg-green-200 rounded-[3vw]">
                    <p className="font-semibold">{node.nodeName}</p>
                    <p className='text-gray-500 text-xs'>Status: {node.status}</p>
                    <p className='text-gray-500 text-xs'>Node Id: {node.nodeId}</p>
                    <p className='text-gray-500 text-xs'>Assigned Models: {node.assignedModels}</p>
                </div>
            );
        });
    }

    return (
        <div className="my-4 p-4">
            <h2 className="text-xl font-bold mb-4">My Nodes</h2>
            {renderedContent}
        </div>
    )
}