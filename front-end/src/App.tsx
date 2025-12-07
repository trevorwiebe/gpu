import './App.css'
import NavBar from './components/NavBar'
import HuggingFaceModels from './components/HuggingFaceModels'
import Library from './components/Library'

import { BrowserRouter, Routes, Route, Navigate } from 'react-router'

function App() {

  return (
    <>
      <BrowserRouter>
        <NavBar/>
        <Routes>
          <Route path="/" element={<Navigate to="/models" replace/>}/>
          <Route path="models" element={<HuggingFaceModels/>}/>
          <Route path="hosted" element={<Library/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App