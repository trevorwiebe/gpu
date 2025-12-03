import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { ModelSortState } from '@/types'

const modelSortSlice = createSlice({
    name: 'modelUi',
    initialState: {
        sortBy: 'downloads',
        sortOrder: 'asc'
    } as ModelSortState,
    reducers: {
        sortModels: (state, action: PayloadAction<string>) => {
            const sortBy = action.payload;

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
        },
    },
});

export const { sortModels } = modelSortSlice.actions;
export default modelSortSlice.reducer

