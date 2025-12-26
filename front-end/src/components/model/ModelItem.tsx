import {numberFormatter} from '../../utils/numberFormat'
import {dateFormatter} from '../../utils/dateFormat'
import Chip from '../Chip';
import { Model } from '../../types';
import Button from '../small/Button'

interface ModelItemProps {
    model: Model;
    authenticated: Boolean | undefined;
    inLibrary: Boolean,
    onFavorite: (model: Model, favorite: Boolean) => void
}

export default function ModelItem(props: ModelItemProps) {

    const {_id, id, downloads, likes, createdAt, gated} = props.model;

    const addToLibraryBtn = <Button 
        title="Add to Library" 
        onClick={ () => props.onFavorite(props.model, !props.inLibrary)}
        className="border-green-900 text-green-900 hover:bg-gray-200 hover:shadow-md"
    />

    const removeFromLibraryBtn = <Button 
        title="Remove from Library" 
        onClick={ () => props.onFavorite(props.model, !props.inLibrary) }
        className="border-green-900 text-white bg-green-900 hover:bg-green-800 hover:shadow-md"
    />
    
    return (
        <div className="rounded-[3vw] shadow-sm p-4 m-2">
            <div className='flex flex-box justify-between'>
                <p className="mb-2">{id}</p>
                <div>
                    {props.authenticated && (props.inLibrary ? removeFromLibraryBtn : addToLibraryBtn)}
                </div>
            </div>
            <div>
                <Chip label={"Downloads"} text={numberFormatter(downloads)}/>
                <Chip label={"Likes"} text={numberFormatter(likes)}/>
                <Chip label={"Created"} text={dateFormatter(createdAt)}/>
                <Chip label={"Access"} text={gated ? "Gated" : "Open"}/>
            </div>
        </div>
    )
}