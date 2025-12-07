interface ButtonProps{
    title: string;
    onClick: () => void;
    className?: string;
}

export default function Button({title, onClick, className}: ButtonProps){

    const baseStyles = "px-3 py-1 mb-2 border rounded-full duration-300 cursor-pointer"
    const combinedClasses = `${baseStyles} ${className || ''}`.trim();

    return ( 
        <button onClick={onClick} className={combinedClasses}>
            {title}
        </button>
    )
}
