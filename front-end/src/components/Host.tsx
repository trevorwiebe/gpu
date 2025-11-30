import ModelList from './model/ModelList'
import Sorter from './Sorter'

export default function Host() {
    return (
        <div className="w-full max-w-md md:max-w-xl lg:max-w-4xl mx-auto">
            <Sorter/>
            <ModelList/>
        </div>
    )
}