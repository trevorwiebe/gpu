import './App.css'
import NavBar from './components/NavBar'
import Host from './components/Host'
import Client from './components/Client'

import { BrowserRouter, Routes, Route, Navigate } from 'react-router'

function App() {

  return (
    <>
      <BrowserRouter>
        <NavBar/>
        <Routes>
          <Route path="/" element={<Navigate to="/host" replace/>}/>
          <Route path="host" element={<Host/>}/>
          <Route path="client" element={<Client/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App