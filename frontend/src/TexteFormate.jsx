/**
 * Affiche le texte d'une réponse en gérant un mini-format :
 *   **texte**  -> gras
 *   - élément  -> puce
 *
 * Sécurité : on ne fait JAMAIS de innerHTML / dangerouslySetInnerHTML.
 * React échappe automatiquement le texte, donc même si une réponse contenait
 * "<script>", il serait affiché comme du texte et jamais exécuté (protection XSS).
 */
function avecGras(ligne) {
  // "a **b** c".split(/\*\*/) -> ["a ", "b", " c"] : les morceaux impairs sont en gras
  return ligne.split(/\*\*/).map((morceau, i) =>
    i % 2 === 1 ? <strong key={i}>{morceau}</strong> : morceau,
  )
}

export default function TexteFormate({ texte }) {
  return texte.split('\n').map((ligne, i) => {
    if (ligne.trim() === '') return <div key={i} className="espace" />
    if (ligne.startsWith('- ')) return <div key={i} className="puce">• {avecGras(ligne.slice(2))}</div>
    return <div key={i}>{avecGras(ligne)}</div>
  })
}
