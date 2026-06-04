import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { PCView } from './views/PCView';
import { MobileView } from './views/MobileView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PCView />} />
        <Route path="/mobile" element={<MobileView />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;