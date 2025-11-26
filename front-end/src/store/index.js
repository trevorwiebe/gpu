import { configureStore } from '@reduxjs/toolkit'
import { modelsReducer } from './slices/modelsSlice'
import { fetchModels } from './thunks/fetchModels'

export const store = configureStore({
    reducer: {
        models: modelsReducer
    }
})

export default store

export { fetchModels }