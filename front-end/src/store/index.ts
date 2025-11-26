import { configureStore } from '@reduxjs/toolkit'
import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux'
import { modelsReducer } from './slices/modelsSlice'
import { fetchModels } from './thunks/fetchModels'

export const store = configureStore({
    reducer: {
        models: modelsReducer
    }
})

export default store

// Export typed hooks
export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof store.getState>
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector

// Export thunks
export { fetchModels }