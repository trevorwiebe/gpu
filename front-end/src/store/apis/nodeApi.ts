import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const nodeApi = createApi({
    reducerPath: 'node',
    baseQuery: fetchBaseQuery({
        baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
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
            }),
            assignModelToNode: build.mutation({
                query: ({userId, nodeId, modelId}) => ({
                    url: '/user/me/node/assign-model',
                    method: 'POST',
                    body: { userId, nodeId, modelId }
                }),
                invalidatesTags: ['node']
            })
        }
    }
});

export const {
    useAuthenticateNodeMutation,
    useFetchNodesQuery,
    useAssignModelToNodeMutation
 } = nodeApi;
export { nodeApi };
