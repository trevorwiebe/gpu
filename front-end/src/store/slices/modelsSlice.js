import { createSlice } from '@reduxjs/toolkit';
import { fetchModels } from '../thunks/fetchModels';

const initialState = {
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
        sortModels: (state, action) => {
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

                const valueA = a[sortBy];
                const valueB = b[sortBy];

                if(sortBy == "createdAt"){
                    if(sortOrder == 'asc'){
                        return new Date(valueB) - new Date(valueA)
                    }else if(sortOrder == 'desc'){
                        return new Date(valueA) - new Date(valueB)
                    }else{
                        return 0
                    }
                }else{
                    if(sortOrder == 'asc'){
                        return valueB - valueA
                    }else if(sortOrder == 'desc'){
                        return valueA - valueB
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