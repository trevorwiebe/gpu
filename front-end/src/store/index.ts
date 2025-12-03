import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query';
import { modelsApi } from './apis/modelsApi'
import modelSortReducer from './slice/modelsSlice'

export const store = configureStore({
    reducer: {
        [modelsApi.reducerPath]: modelsApi.reducer,
        modelsSort: modelSortReducer
    },
    middleware: (getDefaultMiddleware) => {
        return getDefaultMiddleware()
            .concat(modelsApi.middleware);
    }
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store

export { useFetchModelsQuery } from './apis/modelsApi';
export { sortModels } from './slice/modelsSlice'