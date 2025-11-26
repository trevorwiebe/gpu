import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { fetchModels } from '../thunks/fetchModels';

interface Model {
    id: string;
    name: string;
}

interface ModelsState {
    data: Model[];
    isLoading: boolean;
    error: string | null;
}

const initialState: ModelsState = {
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
            .addCase(fetchModels.fulfilled, (state, action: PayloadAction<Model[]>) => {
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