/** Small, dependency-free formatting helpers shared by views. */

export function percent(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

/** 7 → "07" (the references show two-digit streak numerals). */
export function pad2(n) {
  return String(n ?? 0).padStart(2, '0')
}

export function greeting(date = new Date()) {
  const hour = date.getHours()
  if (hour < 5) return 'Still up'
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
const UNITS = [
  ['year', 31536000],
  ['month', 2592000],
  ['week', 604800],
  ['day', 86400],
  ['hour', 3600],
  ['minute', 60],
]

export function timeAgo(iso, now = Date.now()) {
  const seconds = Math.round((new Date(iso).getTime() - now) / 1000)
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit)
  }
  return 'just now'
}

/** "2026-11-13" → "F" (weekday initial), parsed as a local calendar date. */
export function weekdayInitial(isoDate) {
  const [y, m, d] = isoDate.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('en', { weekday: 'narrow' })
}

export function longDate(isoDate) {
  const [y, m, d] = isoDate.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('en', { weekday: 'long', day: 'numeric', month: 'long' })
}

export function browserTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  } catch {
    return 'UTC'
  }
}

/**
 * Only allow redirects to paths inside this app ("/dashboard"), never to
 * another site ("//evil.com", "https://…") — prevents open redirects via
 * ?redirect= on the login page.
 */
export function safeRedirect(value, fallback = '/dashboard') {
  if (typeof value !== 'string') return fallback
  if (!value.startsWith('/') || value.startsWith('//') || value.startsWith('/\\')) return fallback
  return value
}
