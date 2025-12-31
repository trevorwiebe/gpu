import HardwareList from "./hosted/NodeList"
import LibraryModelList from "./hosted/LibraryModelList"

export default function Hosted() {
    return (
        <div className="flex flex-row w-full max-w-2xl md:max-w-4xl lg:max-w-6xl mx-auto">
            <div className="w-2/3">
                <LibraryModelList />
            </div>
            <div className="w-1/3">
                <HardwareList/>
            </div>
        </div>
    )
}