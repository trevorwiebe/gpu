import {numberFormatter} from '../../utils/numberFormat'
import {dateFormatter} from '../../utils/dateFormat'
import Chip from '../Chip';

export default function ModelItem(props) {

    const {id, downloads, likes, createdAt} = props.name;

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