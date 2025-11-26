import { createSlice } from '@reduxjs/toolkit';
import { fetchModels } from '../thunks/fetchModels';

const initialState = {
    data: [],
    isLoading: false,
    error: null
};

const modelsSlice = createSlice({
    name: 'models',
    initialState,
    reducers: {},
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

export const modelsReducer = modelsSlice.reducer;