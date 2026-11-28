/**
 * Lets a page tell the public header which surface it's sitting on, so the
 * header can turn dark while it's over the landing page's dark hero and go
 * back to paper once the hero has scrolled away.
 *
 *   headerSurface.value = 'ink'   // header over a dark section
 *   headerSurface.value = null    // header uses the page's own surface
 */
import { ref } from 'vue'

export const headerSurface = ref(null)
