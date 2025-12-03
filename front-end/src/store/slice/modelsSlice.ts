import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { ModelSortState, SortPayload } from '@/types'

const modelSortSlice = createSlice({
    name: 'modelUi',
    initialState: {
        sortBy: 'downloads',
        sortOrder: 'asc'
    } as ModelSortState,
    reducers: {
        sortModels: (state, action: PayloadAction<SortPayload>) => {
            const { sortBy } = action.payload;

            let sortOrder = state.sortOrder
            if(sortBy == state.sortBy){
                if(sortOrder == "asc"){
                    sortOrder = "desc"
                }else{
                    sortOrder = "asc"
                }
            }else{
                sortOrder = "asc"
            }

            state.sortBy = sortBy;
            state.sortOrder = sortOrder;

            // state.data.sort((a, b) => {

            //     const valueA = a[sortBy as keyof typeof a];
            //     const valueB = b[sortBy as keyof typeof b];

            //     if(sortBy == "createdAt"){
            //         if(sortOrder == 'asc'){
            //             return new Date(valueB as string).getTime() - new Date(valueA as string).getTime()
            //         }else if(sortOrder == 'desc'){
            //             return new Date(valueA as string).getTime() - new Date(valueB as string).getTime()
            //         }else{
            //             return 0
            //         }
            //     }else{
            //         if(sortOrder == 'asc'){
            //             return (valueB as number) - (valueA as number)
            //         }else if(sortOrder == 'desc'){
            //             return (valueA as number) - (valueB as number)
            //         }else{
            //             return 0
            //         }
            //     }
            // });
        },
    },
});

export const { sortModels } = modelSortSlice.actions;
export default modelSortSlice.reducer

