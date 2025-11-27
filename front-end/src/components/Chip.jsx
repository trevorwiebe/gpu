export default function Chip({label, text}){
    return <span className="rounded-full bg-green-900 py-1 px-2 mx-1 text-white text-sm">{label} - {text}</span>
}