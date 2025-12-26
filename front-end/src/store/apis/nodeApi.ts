import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const nodeApi = createApi({
    reducerPath: 'node',
    baseQuery: fetchBaseQuery({
        baseUrl: 'http://localhost:8000'
    }),
    tagTypes: ['node'],
    endpoints (build){
        return {
            authenticateNode: build.mutation({
                query: ({userId, setupToken}) => ({
                    url: '/user/me/node/authenticate',
                    method: 'POST',
                    body: {
                        userId,
                        setupToken
                    }
                }),
                invalidatesTags: ['node']
            }),
            fetchNodes: build.query({
                query: (userId) => {
                    return {
                        url: '/user/me/nodes',
                        params: {
                            userId: userId,
                        },
                        method: 'GET'
                    }
                },
                providesTags: ['node']
            })
        }
    }
});

export const {
    useAuthenticateNodeMutation,
    useFetchNodesQuery
 } = nodeApi;
export { nodeApi };
