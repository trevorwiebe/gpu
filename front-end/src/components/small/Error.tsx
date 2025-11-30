interface ErrorProps {
    text: string;
}

export default function Error({text}: ErrorProps) {
    return (
        <div className="m-10">
            <p className="text-center text-lg text-red-600">{text}</p>
        </div>
    )
}