import {numberFormatter} from '../../utils/numberFormat'
import {dateFormatter} from '../../utils/dateFormat'
import Chip from '../Chip';
import { HuggingFaceModel } from '../../types';

interface ModelItemProps {
    name: HuggingFaceModel;
}

export default function ModelItem(props: ModelItemProps) {

    const {_id, id, downloads, likes, createdAt} = props.name;

    console.log(_id, id);
    
    return (
        <div className="rounded-md shadow-sm p-4 m-2">
            <p className="mb-2">{id}</p>
            <div>
                <Chip label={"Downloads"} text={numberFormatter(downloads)}/>
                <Chip label={"Likes"} text={numberFormatter(likes)}/>
                <Chip label={"Created"} text={dateFormatter(createdAt)}/>
            </div>
        </div>
    )
}