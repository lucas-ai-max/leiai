import { Routes, Route } from 'react-router-dom'
import LandingPage from './LandingPage'
import Dashboard from './Dashboard'
import SalesforceImport from './SalesforceImport'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/projetos" element={<Dashboard />} />
      <Route path="/salesforce" element={<SalesforceImport />} />
    </Routes>
  )
}

export default App
