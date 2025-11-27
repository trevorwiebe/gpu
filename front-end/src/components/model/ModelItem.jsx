import {useState} from 'react';
import {numberFormatter} from '../../utils/numberFormat'
import {dateFormatter} from '../../utils/dateFormat'
import Chip from '../Chip';

export default function ModelItem(props) {

    const [open, setOpen] = useState(false)

    const handleClick = () => (
        setOpen(!open)
    )

    const {id, downloads, likes, createdAt} = props.name;

    const openContent = <div>
        <Chip label={"Downloads"} text={numberFormatter(downloads)}/>
        <Chip label={"Likes"} text={numberFormatter(likes)}/>
        <Chip label={"Created"} text={dateFormatter(createdAt)}/>
    </div>

    return (
        <div className="rounded-md shadow-sm hover:shadow-md p-4 m-2 duration-300" onClick={handleClick}>
            <p className="mb-2">{id}</p>
            {openContent}
        </div>
    )
}