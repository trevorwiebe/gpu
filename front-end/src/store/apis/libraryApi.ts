import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const libraryApi = createApi({
    reducerPath: 'library',
    baseQuery: fetchBaseQuery({
        baseUrl: 'http://localhost:3000'
    }),
    tagTypes: ['library'],
    endpoints (build){
        return {
            fetchLibrary: build.query({
                query: (userId) => {
                    return {
                        url: '/library',
                        params: {
                            userId: userId,
                        },
                        method: 'GET'
                    }
                },
                providesTags: ['library']
            }),
            addToLibrary: build.mutation({
                query: ({userId, modelId}) => ({
                    url: '/library',
                    method: 'POST',
                    body: {
                        userId, 
                        modelId
                    }
                }),
                invalidatesTags: ['library']
            }),
            removeFromLibrary: build.mutation({
                query: (id) => ({
                    url: `/library/${id}`,
                    method: 'DELETE'
                }),
                invalidatesTags: ['library']
            })
        }
    }
});

export const { 
    useFetchLibraryQuery,
    useAddToLibraryMutation,
    useRemoveFromLibraryMutation
 } = libraryApi;
export { libraryApi };