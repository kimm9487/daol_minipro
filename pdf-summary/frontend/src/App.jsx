import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import PdfSummary from './components/PdfSummary';
import Login from './components/Login';
import Register from './components/Register'; // 회원가입 컴포넌트 추가

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PdfSummary />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  );
}

export default App;