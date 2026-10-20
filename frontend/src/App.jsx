import { useEffect, useRef, useState } from 'react'
import TexteFormate from './TexteFormate.jsx'

// Adresse du backend Flask (le port 5001 du Mac est relié au port 5000 du conteneur)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

const MESSAGE_ACCUEIL = {
  auteur: 'bot',
  texte: "Bonjour ! 👋 Je suis l'assistant virtuel de l'ESIC.\nPosez-moi vos questions sur les emplois du temps, les procédures, les services du campus ou le règlement.",
}

// sessionStorage = mémoire du navigateur qui dure le temps de l'onglet (US-002).
// On l'entoure de try/catch car certains navigateurs (navigation privée) peuvent la bloquer.
function lireStockage(cle, valeurParDefaut) {
  try {
    const valeur = sessionStorage.getItem(cle)
    return valeur ? JSON.parse(valeur) : valeurParDefaut
  } catch {
    return valeurParDefaut
  }
}

function ecrireStockage(cle, valeur) {
  try {
    sessionStorage.setItem(cle, JSON.stringify(valeur))
  } catch {
    /* stockage indisponible : l'historique ne sera simplement pas conservé */
  }
}

// Identifiant ANONYME de conversation : un nombre aléatoire, aucune donnée personnelle (RGPD).
// crypto.randomUUID n'existe pas dans les anciens navigateurs : on prévoit une solution de secours.
const nouvelleSession = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : Date.now().toString(36) + Math.random().toString(36).slice(2)

export default function App() {
  // useState = une "variable" dont le changement redessine l'écran
  const [sessionId, setSessionId] = useState(() => lireStockage('sessionId', nouvelleSession()))
  const [messages, setMessages] = useState(() => {
    const sauvegarde = lireStockage('messages', null)
    return Array.isArray(sauvegarde) && sauvegarde.length > 0 ? sauvegarde : [MESSAGE_ACCUEIL]
  })
  const [saisie, setSaisie] = useState('')
  const [enCours, setEnCours] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [consentement, setConsentement] = useState(() => lireStockage('consentement', false))
  const finDuChat = useRef(null)

  // useEffect = "fais ceci quand… change". Ici : sauvegarde à chaque changement.
  // ⚠️ Toujours des accolades { } : sans elles, la flèche RENVOIE le résultat de la fonction,
  // et React croit que c'est une fonction de "nettoyage" à appeler plus tard.
  useEffect(() => { ecrireStockage('messages', messages) }, [messages])
  useEffect(() => { ecrireStockage('sessionId', sessionId) }, [sessionId])
  useEffect(() => { ecrireStockage('consentement', consentement) }, [consentement])

  // Défile automatiquement vers le dernier message
  useEffect(() => { finDuChat.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, enCours])

  // Au démarrage : on récupère les questions fréquentes (US-005)
  useEffect(() => {
    fetch(`${API_URL}/api/suggestions`)
      .then((r) => r.json())
      .then((d) => setSuggestions(Array.isArray(d.suggestions) ? d.suggestions : []))
      .catch(() => setSuggestions([]))
  }, [])

  async function envoyer(texte) {
    const question = texte.trim()
    if (!question || enCours) return
    setMessages((m) => [...m, { auteur: 'user', texte: question }])
    setSaisie('')
    setEnCours(true)

    try {
      const reponse = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question, session_id: sessionId }),
      })
      const donnees = await reponse.json()
      setMessages((m) => [
        ...m,
        donnees.erreur
          ? { auteur: 'bot', texte: donnees.erreur, erreur: true }
          : { auteur: 'bot', texte: donnees.reponse, suggestions: donnees.suggestions, statut: donnees.statut },
      ])
    } catch {
      setMessages((m) => [...m, { auteur: 'bot', texte: 'Le serveur ne répond pas. Réessayez dans un instant. 🔌', erreur: true }])
    } finally {
      setEnCours(false)
    }
  }

  // US-003 : redémarrer proprement = nouvel identifiant + historique vidé
  function redemarrer() {
    setSessionId(nouvelleSession())
    setMessages([MESSAGE_ACCUEIL])
  }

  return (
    <div className="app">
      <header className="entete">
        <div>
          <h1>🎓 Assistant ESIC</h1>
          <p>Réponses 24h/24 sur la vie du campus</p>
        </div>
        <button className="bouton-secondaire" onClick={redemarrer} title="Nouvelle conversation">
          ↻ Nouvelle conversation
        </button>
      </header>

      <main className="chat">
        {messages.map((msg, i) => (
          <div key={i} className={`ligne ${msg.auteur}`}>
            <div className={`bulle ${msg.auteur} ${msg.erreur ? 'erreur' : ''} ${msg.statut === 'bloque' ? 'bloque' : ''}`}>
              <TexteFormate texte={msg.texte} />
              {msg.suggestions?.length > 0 && (
                <div className="puces-suggestions">
                  {msg.suggestions.map((s) => (
                    <button key={s} onClick={() => envoyer(s)}>{s}</button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {enCours && (
          <div className="ligne bot">
            <div className="bulle bot ecrit">● ● ●</div>
          </div>
        )}
        <div ref={finDuChat} />
      </main>

      {messages.length <= 1 && suggestions.length > 0 && (
        <section className="suggestions-depart">
          <p>Questions fréquentes :</p>
          <div className="puces-suggestions">
            {suggestions.map((s) => (
              <button key={s} onClick={() => envoyer(s)}>{s}</button>
            ))}
          </div>
        </section>
      )}

      {/* onSubmit : appelé quand on appuie sur Entrée ou sur le bouton Envoyer */}
      <form className="saisie" onSubmit={(e) => { e.preventDefault(); envoyer(saisie) }}>
        <input
          value={saisie}
          onChange={(e) => setSaisie(e.target.value)}
          placeholder="Posez votre question…"
          maxLength={500}
          aria-label="Votre question"
        />
        <button type="submit" disabled={enCours || !saisie.trim()}>Envoyer</button>
      </form>

      {!consentement && (
        <div className="bandeau-rgpd">
          <span>🔒 Vos questions sont enregistrées <strong>de façon anonyme</strong> pour améliorer le service (conservation 6 mois).</span>
          <button onClick={() => setConsentement(true)}>J'ai compris</button>
        </div>
      )}
    </div>
  )
}
