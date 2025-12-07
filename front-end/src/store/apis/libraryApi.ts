import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const libraryApi = createApi({
    reducerPath: 'library',
    baseQuery: fetchBaseQuery({
        baseUrl: 'http://localhost:8000'
    }),
    tagTypes: ['library'],
    endpoints (build){
        return {
            fetchLibrary: build.query({
                query: (userId) => {
                    return {
                        url: '/user/me/library',
                        params: {
                            userId: userId,
                        },
                        method: 'GET'
                    }
                },
                providesTags: ['library']
            }),
            setInLibrary: build.mutation({
                query: ({userId, modelId, isSet}) => ({
                    url: '/user/me/library',
                    method: 'POST',
                    body: {
                        userId, 
                        modelId,
                        isSet
                    }
                }),
                invalidatesTags: ['library']
            })
        }
    }
});

export const { 
    useFetchLibraryQuery,
    useSetInLibraryMutation
 } = libraryApi;
export { libraryApi };