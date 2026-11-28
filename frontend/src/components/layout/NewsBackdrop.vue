<script setup>
/**
 * The Newspaper theme's "life": tiny paper planes folded from newsprint, gliding
 * across the page behind the content. Each plane swoops on its own height and
 * speed; a couple fly the other way and one does a loop-the-loop.
 *
 * SVG + CSS only. The planes sit behind cards and text (they pass under them),
 * and with reduced motion the global rule stops the flights, leaving the page
 * still.
 */

/** Each flight: height on screen, size, route, speed, start offset, direction. */
const PLANES = [
  { top: '14%', size: 46, route: 'swoop', duration: 26, delay: -2 },
  { top: '38%', size: 34, route: 'glide', duration: 34, delay: -14 },
  { top: '62%', size: 52, route: 'loop', duration: 30, delay: -21 },
  { top: '24%', size: 30, route: 'glide', duration: 40, delay: -30, reverse: true },
  { top: '80%', size: 40, route: 'swoop', duration: 36, delay: -9, reverse: true },
  { top: '50%', size: 28, route: 'swoop', duration: 44, delay: -36 },
  { top: '8%', size: 36, route: 'glide', duration: 31, delay: -24 },
].map((p, i) => ({
  ...p,
  key: i,
  style: {
    top: p.top,
    width: `${p.size}px`,
    animationName: `news-${p.route}${p.reverse ? '-back' : ''}`,
    animationDuration: `${p.duration}s`,
    animationDelay: `${p.delay}s`,
  },
}))
</script>

<template>
  <div class="news" aria-hidden="true">
    <svg width="0" height="0" class="absolute">
      <defs>
        <!-- Rows of tiny print, clipped to each wing. -->
        <pattern id="news-print" width="6" height="3.2" patternUnits="userSpaceOnUse" patternTransform="rotate(12)">
          <rect width="5" height="0.9" y="1" fill="#111" opacity="0.32" />
        </pattern>
        <clipPath id="news-wing-top"><polygon points="2,6 62,19 22,21" /></clipPath>
        <clipPath id="news-wing-low"><polygon points="22,21 62,19 8,36" /></clipPath>
      </defs>
    </svg>

    <div v-for="p in PLANES" :key="p.key" class="plane" :style="p.style">
      <svg viewBox="0 0 64 40" :class="{ flip: p.reverse }" class="plane-art">
        <!-- lower wing, keel fold, upper wing (nose points right) -->
        <polygon points="22,21 62,19 8,36" fill="#ecebe5" />
        <rect width="64" height="40" fill="url(#news-print)" clip-path="url(#news-wing-low)" />
        <polygon points="22,21 62,19 27,29" fill="#cfcdc5" />
        <polygon points="2,6 62,19 22,21" fill="#fbfaf6" />
        <rect width="64" height="40" fill="url(#news-print)" clip-path="url(#news-wing-top)" />
        <!-- a little headline block on the wing -->
        <polygon points="12,10 30,14 24,15 10,12" fill="#111" opacity="0.75" />
        <polygon points="2,6 62,19 22,21" fill="none" stroke="#111" stroke-width="0.6" stroke-opacity="0.55" stroke-linejoin="round" />
        <polygon points="22,21 62,19 8,36" fill="none" stroke="#111" stroke-width="0.6" stroke-opacity="0.45" stroke-linejoin="round" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.news {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}
.plane {
  position: absolute;
  left: 0;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out; /* per segment, so each swoop eases */
  filter: drop-shadow(0 6px 6px rgb(17 17 17 / 0.12));
}
.plane-art {
  display: block;
  width: 100%;
  height: auto;
}
.flip {
  transform: scaleX(-1);
}
</style>

<style>
/* Flight routes (global so the inline animation-name can find them). */
@keyframes news-glide {
  0% { transform: translate(-12vw, 0) rotate(-4deg); }
  25% { transform: translate(18vw, -2vh) rotate(2deg); }
  50% { transform: translate(48vw, 1vh) rotate(-3deg); }
  75% { transform: translate(78vw, -2vh) rotate(3deg); }
  100% { transform: translate(112vw, 0) rotate(-2deg); }
}
@keyframes news-swoop {
  0% { transform: translate(-12vw, 0) rotate(-8deg); }
  20% { transform: translate(12vw, -5vh) rotate(6deg); }
  40% { transform: translate(36vw, 4vh) rotate(-7deg); }
  60% { transform: translate(60vw, -4vh) rotate(7deg); }
  80% { transform: translate(86vw, 5vh) rotate(-6deg); }
  100% { transform: translate(112vw, 0) rotate(4deg); }
}
/* Climbs into a full loop mid-flight, then carries on. */
@keyframes news-loop {
  0% { transform: translate(-12vw, 0) rotate(-3deg); }
  38% { transform: translate(38vw, 0) rotate(0deg); }
  43% { transform: translate(44vw, -5vh) rotate(-90deg); }
  48% { transform: translate(40vw, -10vh) rotate(-180deg); }
  53% { transform: translate(36vw, -5vh) rotate(-270deg); }
  58% { transform: translate(42vw, 0) rotate(-360deg); }
  100% { transform: translate(112vw, -2vh) rotate(-363deg); }
}
/* The same routes flown right-to-left (the plane art is mirrored). */
@keyframes news-glide-back {
  0% { transform: translate(112vw, 0) rotate(4deg); }
  25% { transform: translate(78vw, -2vh) rotate(-2deg); }
  50% { transform: translate(48vw, 1vh) rotate(3deg); }
  75% { transform: translate(18vw, -2vh) rotate(-3deg); }
  100% { transform: translate(-12vw, 0) rotate(2deg); }
}
@keyframes news-swoop-back {
  0% { transform: translate(112vw, 0) rotate(8deg); }
  20% { transform: translate(86vw, -5vh) rotate(-6deg); }
  40% { transform: translate(60vw, 4vh) rotate(7deg); }
  60% { transform: translate(36vw, -4vh) rotate(-7deg); }
  80% { transform: translate(12vw, 5vh) rotate(6deg); }
  100% { transform: translate(-12vw, 0) rotate(-4deg); }
}
</style>
