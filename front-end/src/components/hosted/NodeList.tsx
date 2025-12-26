import { 
    useFetchNodesQuery
} from '../../store';

import { useUser } from "@clerk/clerk-react";

interface NodeModel {
    nodeId: string,
    userId: string,
    status: boolean
}

export default function NodeList(){

    const { user, isSignedIn } = useUser();

    const {
        data: nodeData,
        error: nodeError,
        isLoading: nodesLoading
    } = useFetchNodesQuery(user?.id, {skip: !user?.id});

    if(!isSignedIn) return

    var renderedContent

    if (nodesLoading) {
        renderedContent = <div>Loading nodes...</div>
    } else if (nodeError) {
        renderedContent = <div className="text-red-500">Error loading nodes</div>
    } else if (!nodeData || nodeData.length === 0) {
        renderedContent = <div>No nodes authenticated</div>
    } else {
        renderedContent = nodeData.map((node: NodeModel) => {
            return (
                <div key={node.nodeId} className="my-2 p-2 bg-green-200 rounded-full">
                    <p>{node.status}</p>
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