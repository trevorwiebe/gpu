import { NodeModel } from "@/types";

interface AssignedNodeChipsProps {
    modelId: string;
    selectedNodes: NodeModel[];
}

export default function AssignedNodeChips({ modelId, selectedNodes }: AssignedNodeChipsProps) {

    return (
        <div className="flex flex-wrap gap-2 mt-2 h-6 items-center">
            <p className="text-xs">Active Nodes: </p>
            {selectedNodes.map(node => (
                <div
                    key={node.nodeId}
                    className="px-3 py-1 bg-green-900 text-white text-xs rounded-full"
                >
                    {node.nodeName}
                </div>
            ))}
        </div>
    );
}
