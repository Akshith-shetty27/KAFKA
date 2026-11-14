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

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(code, lang) {
    return `<pre class="k-code"><code class="hljs language-${escapeHtml(lang || 'text')}">${highlight(code, lang)}</code></pre>`
  },
})

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
