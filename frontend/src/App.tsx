import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-red-600 text-white py-6 shadow-md">
          <div className="container mx-auto px-4">
            <h1 className="text-3xl font-bold">OpenShift Operator Upgrade Advisor</h1>
            <p className="text-red-100 mt-1">AI-Powered Compatibility Analysis</p>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/results/:analysisId" element={<ResultsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer className="bg-gray-800 text-gray-300 py-4 mt-12">
          <div className="container mx-auto px-4 text-center">
            <p>OpenShift Operator Upgrade Advisor v1.0.0</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
