/**
 * Navigation items for the signed-in app header, in the order of the
 * reference design (HOME · PREPARE · PRACTICE · PROGRESS · ASK KAFKA ·
 * SETTINGS — PROGRESS takes the reference's INTERVIEW slot, decision D10).
 */
export const appNav = [
  { label: 'Home', to: { name: 'dashboard' } },
  { label: 'Prepare', to: { name: 'prepare' } },
  // `match`: path prefixes that also count as "this section" for highlighting.
  { label: 'Practice', to: { name: 'practice', params: { category: 'coding' } }, match: ['/practice', '/questions'] },
  { label: 'Progress', to: { name: 'progress' } },
  { label: 'Ask Kafka', to: { name: 'ask' }, match: ['/ask'] },
  { label: 'Settings', to: { name: 'settings' }, icon: 'settings' },
]

/** Anchor links on the public landing page. */
export const publicNav = [
  { label: 'How it works', to: { name: 'landing', hash: '#method' } },
  { label: 'Tracks', to: { name: 'landing', hash: '#prepare' } },
]
