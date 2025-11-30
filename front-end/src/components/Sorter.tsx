import { useDispatch, useSelector } from 'react-redux'
import { sortModels } from '../store'
import { RootState } from '../types'

import SortChip from './SortChip'

export default function Sorter() {

    const dispatch = useDispatch()

    const { sortBy } = useSelector((state: RootState) => state.models)

    const handleSortBy = (sortBy: string) => {
        dispatch(sortModels({sortBy: sortBy}))
    }

    return (
        <div className="bg-green-100 rounded-full m-2 flex justify-around">
            <SortChip active={sortBy == "downloads"} label={"Sort by Downloads"} onClick={() => handleSortBy("downloads")}/>
            <SortChip active={sortBy == "likes"} label={"Sort by Likes"} onClick={() => handleSortBy("likes")}/>
            <SortChip active={sortBy == "createdAt"} label={"Sort by Created"} onClick={() => handleSortBy("createdAt")}/>    
        </div>
    )
}