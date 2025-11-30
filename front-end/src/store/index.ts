import { configureStore } from '@reduxjs/toolkit'
import { modelsReducer } from './slices/modelsSlice'
import { fetchModels } from './thunks/fetchModels'
import { sortModels } from './slices/modelsSlice'

export const store = configureStore({
    reducer: {
        models: modelsReducer
    }
})

export type AppDispatch = typeof store.dispatch

export default store

export { fetchModels, sortModels }