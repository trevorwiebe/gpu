import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const libraryApi = createApi({
    reducerPath: 'library',
    baseQuery: fetchBaseQuery({
        baseUrl: 'http://localhost:3000'
    }),
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
                }
            })
        }
    }
});

export const { useFetchLibraryQuery } = libraryApi;
export { libraryApi };