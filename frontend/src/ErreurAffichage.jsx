import { Component } from 'react'

/**
 * "Error Boundary" : si un composant plante, React affiche normalement une page blanche.
 * Ce composant attrape l'erreur et affiche un message lisible à la place.
 * (C'est l'un des rares cas où React impose d'écrire une "classe" plutôt qu'une fonction.)
 */
export default class ErreurAffichage extends Component {
  state = { erreur: null }

  static getDerivedStateFromError(erreur) {
    return { erreur }
  }

  reinitialiser = () => {
    try {
      sessionStorage.clear()
    } catch {
      /* stockage indisponible */
    }
    window.location.reload()
  }

  render() {
    if (!this.state.erreur) return this.props.children
    return (
      <div style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 640, margin: '0 auto' }}>
        <h2>Oups, l'interface a rencontré une erreur 😕</h2>
        <p>Message technique (à copier pour le débogage) :</p>
        <pre style={{ background: '#fee2e2', padding: 12, whiteSpace: 'pre-wrap' }}>
          {String(this.state.erreur?.stack || this.state.erreur)}
        </pre>
        <button onClick={this.reinitialiser}>Réinitialiser et recharger</button>
      </div>
    )
  }
}
