import { createAsyncThunk } from "@reduxjs/toolkit"
import axios from 'axios'

const fetchModels = createAsyncThunk('models/fetch', async () => {
    const response = await axios.get("https://huggingface.co/api/models?filter=text-generation&sort=downloads&direction=-1&limit=100&full=true")
    return response.data;
})

export { fetchModels }
