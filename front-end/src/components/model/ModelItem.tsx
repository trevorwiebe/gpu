import {numberFormatter} from '../../utils/numberFormat'
import {dateFormatter} from '../../utils/dateFormat'
import Chip from '../Chip';
import { Model } from '../../types';
import { FaRegHeart, FaHeart } from "react-icons/fa";

interface ModelItemProps {
    model: Model;
    authenticated: Boolean | undefined;
    inLibrary: Boolean,
    onFavorite: (model: Model, favorite: Boolean) => void
}

export default function ModelItem(props: ModelItemProps) {

    const {_id, id, downloads, likes, createdAt} = props.model;
    
    return (
        <div className="rounded-md shadow-sm p-4 m-2">
            <div className='flex flex-box justify-between'>
                <p className="mb-2">{id}</p>
                <div onClick={() => props.onFavorite(props.model, !props.inLibrary)}>
                    {props.authenticated && props.inLibrary ? <FaHeart/> : <FaRegHeart/>}
                </div>
            </div>
            <div>
                <Chip label={"Downloads"} text={numberFormatter(downloads)}/>
                <Chip label={"Likes"} text={numberFormatter(likes)}/>
                <Chip label={"Created"} text={dateFormatter(createdAt)}/>
            </div>
        </div>
    )
}