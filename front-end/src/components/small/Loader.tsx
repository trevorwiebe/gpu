export default function Loader() {
    return (
        <div className="m-10">
            <p className="text-center text-lg my-5">Loading...</p>
            <div className="flex items-center justify-center">
                <div 
                    className="w-8 h-8 border-4 border-green-900 border-t-transparent rounded-full animate-spin"
                    role="status"/>
            </div>
        </div>
    )
}