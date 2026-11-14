/**
 * Navigation items for the signed-in app header. Each later phase adds its
 * page here (Progress, Ask KAFKA) when the page exists, so the nav never
 * links to something that isn't built.
 */
export const appNav = [
  { label: 'Home', to: { name: 'dashboard' } },
  { label: 'Prepare', to: { name: 'prepare' } },
  // `match`: path prefixes that also count as "this section" for highlighting.
  { label: 'Practice', to: { name: 'practice', params: { category: 'coding' } }, match: ['/practice', '/questions'] },
  { label: 'Settings', to: { name: 'settings' }, icon: 'settings' },
]

/** Anchor links on the public landing page. */
export const publicNav = [
  { label: 'Method', to: { name: 'landing', hash: '#method' } },
  { label: 'Prepare', to: { name: 'landing', hash: '#prepare' } },
  { label: 'Ask Kafka', to: { name: 'landing', hash: '#ask-kafka' } },
]
