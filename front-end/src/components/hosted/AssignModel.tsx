import { useState, useEffect } from 'react';
import { NodeModel } from "@/types";
import Button from '../small/Button';

interface AssignModelProps {
    modelId: string;
    nodes: NodeModel[];
    onNodeSelected: (nodeId: string) => void;
}

export default function AssignModel({modelId, nodes, onNodeSelected}: AssignModelProps){

    // This state determines whether or not we should show the confirm button
    const [confirmSelection, onConfirmSelection] = useState<boolean>(false);
    const handleToggleConfirmButton = () => onConfirmSelection(!confirmSelection)

    // This state is responsible for whether or not the dropdown menu is open
    const [isOpen, setIsOpen] = useState(false);
    const handleToggleDropdownOpen = () => setIsOpen(!isOpen);

    // This state is for the selected nodeId and nodeName
    const [selectedNodeId,  setSelectedNodeId] = useState<string | null>(null);
    const [selectedNodeName, setSelectedNodeName] = useState<string | null>(null);

    // We use a useEffect to populate the assigned nodeId and nodeName when the data becomes available
    useEffect(() => {
        const assignedNode = nodes.find(node => node.assignedModels.includes(modelId));
        if (assignedNode) {
            setSelectedNodeId(assignedNode.nodeId);
            setSelectedNodeName(assignedNode.nodeName);
        }
    }, [nodes, modelId]);

    // We call this function when the user makes a selection from the dropdown menu, but has not confirmed it yet.
    const handleDropdownSelect = (nodeId: string) => {
        setSelectedNodeId(nodeId);
        const nodeName = nodes.find(node => node.nodeId === nodeId)?.nodeName || null;
        setSelectedNodeName(nodeName);
        handleToggleConfirmButton();
        handleToggleDropdownOpen();
    }

    // We call this function when the user has confirm the node the want to use to host this model
    const handleNodeSelect = (nodeId: string) =>{
        handleToggleConfirmButton()
        onNodeSelected(nodeId);
    }

    var nodeMenu;

    if (nodes.length === 0) {
        nodeMenu = (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="p-4 text-center text-gray-500">No nodes available</div>
            </div>
        );
    }else{
       nodeMenu = <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
            {nodes.map((node) => {

                let className = "px-4 py-2 transition-colors duration-150";

                if (selectedNodeId) {
                    className += " opacity-50 cursor-not-allowed text-gray-400";
                } else {
                    className += " hover:bg-green-50 cursor-pointer text-gray-700";
                }

                return (
                    <div
                        key={node.nodeId}
                        className={className}
                        onClick={() => !selectedNodeId && handleDropdownSelect(node.nodeId)}
                    >
                        {node.nodeName}
                    </div>
                );
            })}
        </div>
    }

    if(selectedNodeName){
        var buttonClasses = "border-green-900 text-white bg-green-900 hover:bg-green-800 hover:border-green-800"
    }else{
        var buttonClasses = "border-green-900 text-green-900 hover:bg-green-100"
    }

    return (
        <div className="relative">
            <Button
                title={selectedNodeName || "Select Node"}
                onClick={handleToggleDropdownOpen}
                className={buttonClasses}
            />

            {isOpen && (nodeMenu)}

            {confirmSelection && selectedNodeId &&
                <Button
                    title="Confirm"
                    onClick={ () => handleNodeSelect(selectedNodeId)}
                    className="border-green-900 text-white bg-green-900 hover:bg-green-800 hover:border-green-800 ml-2"
                />
            }

        </div>
    );
}