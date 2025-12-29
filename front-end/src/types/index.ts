// Hugging Face API Model interface
export interface Model {
  _id: string;
  id: string;
  modelId: string;
  author: string;
  sha: string;
  lastModified: string;
  tags: string[];
  pipeline_tag: string;
  siblings: Array<{
    rfilename: string;
    [key: string]: unknown;
  }>;
  private: boolean;
  gated: string | false;
  downloads: number;
  likes: number;
  library_name: string;
  createdAt: string;
  cardData?: {
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

// User library object
export interface LibraryModel {
    modelId: string,
    userId: string,
    huggingFaceModelId: string,
    modelName: string,
    health: boolean
}

export interface NodeModel {
    nodeId: string,
    userId: string,
    status: boolean,
    nodeName: string,
    assignedModels: string[],
    modelStatus?: string,      // "idle", "downloading", "loading", "ready", "error"
    activeModel?: string,       // Currently active model ID
    activeModelName?: string    // Currently active model name
}

// Redux State interface
export interface ModelSortState {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

// Root State interface
export interface RootState {
  modelsSort: ModelSortState;
}