import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './layouts/App.jsx'
import './styles/index.css' // <-- ตรวจสอบว่ามีบรรทัดนี้

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
