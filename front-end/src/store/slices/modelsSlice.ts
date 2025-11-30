import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { fetchModels } from '../thunks/fetchModels';
import { ModelsState, SortPayload } from '../../types';

const initialState: ModelsState = {
    data: [],
    sortBy: "downloads",
    sortOrder: "desc",
    isLoading: false,
    error: null
};

const modelsSlice = createSlice({
    name: 'models',
    initialState,
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

            state.data.sort((a, b) => {

                const valueA = a[sortBy as keyof typeof a];
                const valueB = b[sortBy as keyof typeof b];

                if(sortBy == "createdAt"){
                    if(sortOrder == 'asc'){
                        return new Date(valueB as string).getTime() - new Date(valueA as string).getTime()
                    }else if(sortOrder == 'desc'){
                        return new Date(valueA as string).getTime() - new Date(valueB as string).getTime()
                    }else{
                        return 0
                    }
                }else{
                    if(sortOrder == 'asc'){
                        return (valueB as number) - (valueA as number)
                    }else if(sortOrder == 'desc'){
                        return (valueA as number) - (valueB as number)
                    }else{
                        return 0
                    }
                }
            });
        }
    },
    extraReducers(builder) {
        builder
            .addCase(fetchModels.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(fetchModels.fulfilled, (state, action) => {
                state.isLoading = false;
                state.data = action.payload;
                state.error = null;
            })
            .addCase(fetchModels.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.error.message || 'Something went wrong';
            });
    }
});

export const { sortModels } = modelsSlice.actions;
export const modelsReducer = modelsSlice.reducer;