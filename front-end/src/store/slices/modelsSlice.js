import { createSlice } from '@reduxjs/toolkit';
import { fetchModels } from '../thunks/fetchModels';

const initialState = {
    data: [],
    sortBy: "",
    sortOrder: "",
    isLoading: false,
    error: null
};

const modelsSlice = createSlice({
    name: 'models',
    initialState,
    reducers: {
        sortModels: (state, action) => {
            const { sortBy } = action.payload;

            const sortOrder = "desc";

            state.sortBy = sortBy;
            state.sortOrder = sortOrder;

            state.data.sort((a, b) => {
                const valueA = a[sortBy];
                const valueB = b[sortBy];

                if(sortOrder === 'asc'){
                    return valueA - valueB
                }else if(sortOrder === 'desc'){
                   return valueB - valueA
                }else{
                    return 0
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