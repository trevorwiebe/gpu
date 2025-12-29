import { useState, useEffect, useRef } from 'react';
import { NodeModel } from "@/types";
import Button from '../small/Button';

interface AssignModelProps {
    modelId: string;
    nodes: NodeModel[];
    onNodeSelected: (nodeId: string) => void;
}

export default function AssignModel({modelId, nodes, onNodeSelected}: AssignModelProps){

    // This state is responsible for whether or not the dropdown menu is open
    const [isOpen, setIsOpen] = useState(false);
    const handleToggleDropdownOpen = () => setIsOpen(!isOpen);

    // This state tracks the currently selected nodeId (before confirmation)
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

    // Ref for the dropdown container to detect outside clicks
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    // We call this function when the user makes a selection from the dropdown menu, but has not confirmed it yet.
    const handleDropdownSelect = (nodeId: string) => {
        setSelectedNodeId(nodeId);
        setIsOpen(false);
    }

    // We call this function when the user confirms they want to assign this model to the selected node
    const handleNodeSelect = () => {
        if (selectedNodeId) {
            onNodeSelected(selectedNodeId);
            setSelectedNodeId(null); // Reset selection after confirmation
        }
    }

    var nodeMenu;

    if (nodes.length === 0) {
        nodeMenu = (
            <div className="absolute right-0 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="p-4 text-gray-500">No authenticated nodes</div>
            </div>
        );
    } else {
        nodeMenu = (
            <div className="absolute right-0 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                {nodes.map((node) => {
                    // Check if this node already has this model assigned
                    const isAssigned = node.activeModelId == modelId

                    let className = "px-4 py-2 transition-colors duration-150";

                    if (isAssigned) {
                        // Gray out nodes that already have this model assigned
                        className += " opacity-50 cursor-not-allowed text-gray-400";
                    } else {
                        className += " hover:bg-green-50 cursor-pointer text-gray-700";
                    }

                    return (
                        <div
                            key={node.nodeId}
                            className={className}
                            onClick={() => !isAssigned && handleDropdownSelect(node.nodeId)}
                        >
                            {node.nodeName}
                        </div>
                    );
                })}
            </div>
        );
    }

    return (
        <div ref={dropdownRef} className="relative">
            <Button
                title="Select Node"
                onClick={handleToggleDropdownOpen}
                className="border-green-900 text-green-900 hover:bg-green-100"
            />

            {isOpen && nodeMenu}

            {selectedNodeId && (
                <Button
                    title={`Confirm ${nodes.find(node => node.nodeId === selectedNodeId)?.nodeName || ''}`}
                    onClick={handleNodeSelect}
                    className="border-green-900 text-white bg-green-900 hover:bg-green-800 hover:border-green-800 ml-2"
                />
            )}
        </div>
    );
}