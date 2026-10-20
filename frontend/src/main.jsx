import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import ErreurAffichage from './ErreurAffichage.jsx'
import './App.css'

// Point d'entrée : React "monte" le composant App dans la <div id="root"> de index.html
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErreurAffichage>
      <App />
    </ErreurAffichage>
  </React.StrictMode>,
)
