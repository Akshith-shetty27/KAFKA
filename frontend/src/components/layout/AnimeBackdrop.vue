<script setup>
/**
 * The Anime theme's scene, behind the whole signed-in app (after the "Mr L
 * Production" reference): a twilight sky melting from deep blue into sakura pink
 * and sunset orange, a glowing sun on the horizon, a snow-capped mountain above a
 * drifting sea of clouds, wisps of pink cloud, a swaying field of pink flowers,
 * and sakura petals blowing across on the wind.
 *
 * SVG + CSS only, drawn in code. A twilight scrim keeps the reading area calm;
 * with reduced motion the global rule stops the motion.
 */

/** Deterministic pseudo-random, so the scene is the same every visit. */
function rand(seed) {
  const x = Math.sin(seed * 17.719 + 2.3) * 43758.5453
  return x - Math.floor(x)
}

// Cloud sea: overlapping puffs in a band below the mountain.
const CLOUDS = Array.from({ length: 34 }, (_, i) => ({
  key: i,
  cx: -100 + rand(i + 1) * 1700,
  cy: 640 + rand(i + 2) * 70,
  rx: 60 + rand(i + 3) * 110,
  ry: 22 + rand(i + 4) * 26,
  fill: rand(i + 5) > 0.5 ? '#f6d9e4' : '#e9c3d6',
  opacity: 0.35 + rand(i + 6) * 0.35,
}))

// Wisps of pink cloud high in the sky.
const WISPS = Array.from({ length: 9 }, (_, i) => ({
  key: i,
  cx: rand(i + 21) * 1440,
  cy: 120 + rand(i + 22) * 260,
  rx: 30 + rand(i + 23) * 60,
  ry: 6 + rand(i + 24) * 8,
}))

// Flower field: clusters of pink blossoms in front, swaying in groups.
const PATCHES = Array.from({ length: 7 }, (_, p) => ({
  key: p,
  origin: `${p * 220 + 100}px 900px`,
  duration: `${4 + rand(p + 41) * 3}s`,
  delay: `${-rand(p + 42) * 4}s`,
  blooms: Array.from({ length: 34 }, (_, i) => {
    const s = p * 100 + i
    return {
      key: i,
      cx: p * 220 - 40 + rand(s + 51) * 300,
      cy: 835 + rand(s + 52) * 70,
      r: 3 + rand(s + 53) * 7,
      fill: ['#ff86ad', '#e0567f', '#ffb0c8', '#b83a6a'][Math.floor(rand(s + 54) * 4)],
    }
  }),
}))

// Sakura petals blowing across on the wind (right to left, falling).
const PETALS = Array.from({ length: 16 }, (_, i) => ({
  key: i,
  style: {
    top: `${rand(i + 71) * 70}%`,
    width: `${8 + rand(i + 72) * 9}px`,
    height: `${8 + rand(i + 72) * 9}px`,
    animationDuration: `${11 + rand(i + 73) * 10}s`,
    animationDelay: `${-rand(i + 74) * 20}s`,
    '--fall': `${20 + rand(i + 75) * 30}vh`,
  },
}))
</script>

<template>
  <div class="anime" aria-hidden="true">
    <div class="sky" />

    <svg class="scene" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice">
      <defs>
        <linearGradient id="an-mount" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#4a4f86" />
          <stop offset="1" stop-color="#262b52" />
        </linearGradient>
        <linearGradient id="an-snow" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#fff1f5" />
          <stop offset="1" stop-color="#d7c9e6" />
        </linearGradient>
        <linearGradient id="an-ground" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#3a1f3f" />
          <stop offset="1" stop-color="#1a1130" />
        </linearGradient>
        <filter id="an-soft"><feGaussianBlur stdDeviation="6" /></filter>
      </defs>

      <!-- wisps of pink cloud -->
      <g class="wisps" filter="url(#an-soft)">
        <ellipse v-for="w in WISPS" :key="w.key" :cx="w.cx" :cy="w.cy" :rx="w.rx" :ry="w.ry" fill="#ff9dbb" fill-opacity="0.35" />
      </g>

      <!-- the mountain, snow cap lit from the sun on the left -->
      <polygon fill="url(#an-mount)" points="700,760 960,520 1030,470 1075,452 1110,455 1150,480 1240,545 1440,690 1440,900 700,900" />
      <polygon
        fill="url(#an-snow)"
        points="1030,470 1075,452 1110,455 1150,480 1180,505 1160,515 1140,500 1120,525 1100,505 1080,530 1060,505 1040,522 1020,500 1000,512"
      />

      <!-- cloud sea, drifting -->
      <g class="cloud-sea" filter="url(#an-soft)">
        <ellipse v-for="c in CLOUDS" :key="c.key" :cx="c.cx" :cy="c.cy" :rx="c.rx" :ry="c.ry" :fill="c.fill" :fill-opacity="c.opacity" />
      </g>

      <!-- hillside and the flower field -->
      <path d="M0 820 Q 360 770 720 815 T 1440 800 L1440 900 L0 900 Z" fill="url(#an-ground)" />
      <g v-for="p in PATCHES" :key="p.key" class="patch" :style="{ transformOrigin: p.origin, animationDuration: p.duration, animationDelay: p.delay }">
        <circle v-for="b in p.blooms" :key="b.key" :cx="b.cx" :cy="b.cy" :r="b.r" :fill="b.fill" fill-opacity="0.6" />
      </g>
    </svg>

    <div class="scrim" />
    <span v-for="p in PETALS" :key="p.key" class="petal" :style="p.style">
      <svg viewBox="0 0 20 20"><path d="M10 1 C 17 4, 19 12, 10 19 C 1 12, 3 4, 10 1 Z" fill="#ff9dbb" /></svg>
    </span>
  </div>
</template>

<style scoped>
.anime {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
  background: #121931;
}
/* Twilight: deep blue overhead into pink and sunset orange at the horizon, with
   the sun glowing low on the left of the mountain. */
.sky {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(7% 9% at 42% 70%, rgb(255 246 220 / 0.95), transparent 70%),
    radial-gradient(30% 22% at 42% 70%, rgb(255 190 140 / 0.45), transparent 75%),
    linear-gradient(180deg, #121931 0%, #1d2a5e 30%, #4a4a8a 52%, #b56a92 66%, #f0a07e 74%, #3b2550 86%, #1a1130 100%);
  animation: glow 10s ease-in-out infinite alternate;
}
@keyframes glow {
  from {
    filter: saturate(0.9) brightness(0.92);
  }
  to {
    filter: saturate(1.1) brightness(1.04);
  }
}
.scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.cloud-sea {
  animation: drift 60s ease-in-out infinite alternate;
}
.wisps {
  animation: drift 90s ease-in-out infinite alternate-reverse;
}
@keyframes drift {
  from {
    transform: translateX(-60px);
  }
  to {
    transform: translateX(60px);
  }
}
.patch {
  animation: sway ease-in-out infinite alternate;
}
@keyframes sway {
  from {
    transform: rotate(-1deg);
  }
  to {
    transform: rotate(1deg);
  }
}
/* Calms the reading area (left side and top), like the reference. */
.scrim {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgb(18 25 49 / 0.82) 0%, rgb(18 25 49 / 0.55) 40%, rgb(18 25 49 / 0.15) 80%),
    linear-gradient(180deg, rgb(18 25 49 / 0.45), transparent 35%, transparent 70%, rgb(18 25 49 / 0.35));
}
.petal {
  position: absolute;
  left: 100%;
  opacity: 0.8;
  animation: blow linear infinite;
}
.petal svg {
  display: block;
  width: 100%;
  height: 100%;
}
@keyframes blow {
  from {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(-60vw, calc(var(--fall) * 0.6)) rotate(260deg);
  }
  to {
    transform: translate(-115vw, var(--fall)) rotate(540deg);
  }
}
</style>
