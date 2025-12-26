interface ChipProps {
    label: string;
    text: string;
}

export default function Chip({label, text}: ChipProps) {
    return <span className="rounded-full bg-green-900 py-1 px-2 mx-1 text-white text-xs">{label} - {text}</span>
}