import { createAsyncThunk } from "@reduxjs/toolkit"
import axios from 'axios'
import { HuggingFaceModel } from '../../types'

const fetchModels = createAsyncThunk<HuggingFaceModel[], void>(
  'models/fetch', 
  async () => {
    const response = await axios.get<HuggingFaceModel[]>("https://huggingface.co/api/models?filter=text-generation&sort=downloads&direction=-1&limit=100&full=true")
    return response.data;
  }
)

export { fetchModels }