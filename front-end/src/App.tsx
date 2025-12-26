import './App.css'
import NavBar from './components/NavBar'
import HuggingFaceModels from './components/HuggingFaceModels'
import Hosted from './components/Hosted'
import Setup from './components/Setup'

import { BrowserRouter, Routes, Route, Navigate } from 'react-router'

function App() {

  return (
    <>
      <BrowserRouter>
        <NavBar/>
        <Routes>
          <Route path="/" element={<Navigate to="/models" replace/>}/>
          <Route path="models" element={<HuggingFaceModels/>}/>
          <Route path="hosted" element={<Hosted/>}/>
          <Route path="setup/:setupToken" element={<Setup/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App