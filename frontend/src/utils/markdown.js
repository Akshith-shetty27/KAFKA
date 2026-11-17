/**
 * Markdown → safe HTML.
 *
 * Two layers of protection, because in Phase 5 this also renders AI output:
 *   1. markdown-it runs with `html: false`, so raw HTML in the source is
 *      escaped, not rendered.
 *   2. The result is passed through DOMPurify anyway (defence in depth).
 * Code fences are syntax-highlighted with a small highlight.js build.
 */
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'
import cpp from 'highlight.js/lib/languages/cpp'
import java from 'highlight.js/lib/languages/java'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import sql from 'highlight.js/lib/languages/sql'
import MarkdownIt from 'markdown-it'

hljs.registerLanguage('python', python)
hljs.registerLanguage('java', java)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('sql', sql)

const escapeHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

/** Highlight `code` as `language`; unknown languages are just escaped. */
export function highlight(code, language) {
  if (language && hljs.getLanguage(language)) {
    return hljs.highlight(code, { language, ignoreIllegals: true }).value
  }
  return escapeHtml(code)
}

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

// Code fences: a header bar (language + copy button) above the highlighted code.
// The copy button is handled by a delegated click listener in KMarkdown.
md.renderer.rules.fence = (tokens, idx) => {
  const token = tokens[idx]
  const lang = token.info.trim().split(/\s+/)[0]
  // The info string comes from model output: keep only safe characters for the label/class.
  const label = (lang || '').replace(/[^\w+#.-]/g, '').slice(0, 20) || 'code'
  return (
    `<div class="k-code-block"><div class="k-code-bar"><span>${label}</span>` +
    `<button type="button" class="k-code-copy" data-copy-code aria-live="polite">Copy</button></div>` +
    `<pre class="k-code"><code class="hljs language-${label}">${highlight(token.content, lang)}</code></pre></div>\n`
  )
}

// External links open in a new tab without giving it access to this window.
const defaultLinkOpen = md.renderer.rules.link_open ?? ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet('target', '_blank')
  tokens[idx].attrSet('rel', 'noopener noreferrer')
  return defaultLinkOpen(tokens, idx, options, env, self)
}

export function renderMarkdown(source) {
  return DOMPurify.sanitize(md.render(source ?? ''), { ADD_ATTR: ['target'] })
}
