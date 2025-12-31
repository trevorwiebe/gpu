import ModelList from './model/ModelList'
import Sorter from './Sorter'

export default function HuggingFaceModels() {
    return (
        <div className="w-full max-w-2xl md:max-w-4xl lg:max-w-6xl mx-auto">
            <Sorter/>
            <ModelList/>
        </div>
    )
}