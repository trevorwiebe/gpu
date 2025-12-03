import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Model } from '../../types';

const modelsApi = createApi({
    reducerPath: 'models',
    baseQuery: fetchBaseQuery({
        baseUrl: 'https://huggingface.co/api/'
    }),
    endpoints(builder){
        return {
            fetchModels: builder.query<Model[], void>({
                query: () => ({
                    url: 'models',
                    params: {
                        filter: 'text-generation',
                        sort: 'downloads',
                        direction: '-1',
                        limit: 100,
                        full: true
                    },
                    method: 'GET'
                }),
            }),
        };
    },
});

export const { useFetchModelsQuery } = modelsApi;
export { modelsApi };