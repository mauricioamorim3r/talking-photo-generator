import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AdminPanel from './pages/AdminPanel';
import GalleryPage from './pages/GalleryPage';
import ImageGeneratorPage from './pages/ImageGeneratorPage';
import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/gallery" element={<GalleryPage />} />
          <Route path="/image-generator" element={<ImageGeneratorPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;