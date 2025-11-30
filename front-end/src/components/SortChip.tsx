interface SortChipProps {
    active: boolean;
    label: string;
    onClick: () => void;
}

export default function SortChip({active, label, onClick}: SortChipProps) {

    const baseStyles = 'my-1 px-4 py-1 rounded-full hover:shadow-lg duration-300';
    
    const activeStyles = 'text-white bg-green-900 hover:bg-green-800';
    const inactiveStyles = 'text-gray-700 bg-green-100 hover:text-black hover:bg-green-300';

    const chipClasses = `${baseStyles} ${active ? activeStyles : inactiveStyles}`;

    return (
        <button 
            onClick={onClick}
            className={chipClasses}
        >
            {label}
        </button>
    )
}