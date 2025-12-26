import { NodeModel } from "@/types";

interface AssignedNodeChipsProps {
    modelId: string;
    nodes: NodeModel[];
}

export default function AssignedNodeChips({ modelId, nodes }: AssignedNodeChipsProps) {
    // Find all nodes that have this model assigned
    const assignedNodes = nodes.filter(node => node.assignedModels.includes(modelId));

    if (assignedNodes.length === 0) return null;

    return (
        <div className="flex flex-wrap gap-2 mt-2">
            {assignedNodes.map(node => (
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
