<script setup>
/**
 * The Floral theme's backdrop, behind the whole signed-in app: a plum-to-garden-
 * teal wash, peonies drawn in code at the page edges (rings of shaded petals over
 * teal-green leaves), and a few petals drifting slowly down the screen.
 *
 * Everything is SVG + CSS (no images). The flowers sit at low opacity at the
 * edges so text stays readable; with reduced motion the petals and the flowers'
 * gentle sway stop (global rule).
 */

/** Petal rings from the outside in: count, distance from centre, size, twist. */
const RINGS = [
  { n: 10, dist: 0.56, rx: 0.3, ry: 0.42, twist: 0 },
  { n: 9, dist: 0.44, rx: 0.27, ry: 0.36, twist: 0.35 },
  { n: 8, dist: 0.32, rx: 0.23, ry: 0.3, twist: 0.1 },
  { n: 7, dist: 0.2, rx: 0.19, ry: 0.24, twist: 0.5 },
  { n: 6, dist: 0.1, rx: 0.14, ry: 0.17, twist: 0.2 },
  { n: 4, dist: 0.03, rx: 0.09, ry: 0.11, twist: 0.7 },
]

/** Deterministic jitter so every visit draws the same flower. */
function jitter(seed) {
  const x = Math.sin(seed * 91.7) * 43758.5453
  return x - Math.floor(x) - 0.5
}

function peony(seed) {
  const petals = []
  RINGS.forEach((ring, k) => {
    for (let i = 0; i < ring.n; i++) {
      const j = jitter(seed + k * 13 + i)
      const angle = (360 / ring.n) * (i + ring.twist) + j * 14
      petals.push({
        key: `${k}-${i}`,
        cy: -ring.dist * 100 * (1 + j * 0.12),
        rx: ring.rx * 100 * (1 + j * 0.2),
        ry: ring.ry * 100 * (1 - j * 0.15),
        rotate: angle,
        // Inner rings are a touch lighter, so the bloom reads as cupped.
        fill: k < 2 ? 'url(#petal-deep)' : k < 4 ? 'url(#petal-mid)' : 'url(#petal-light)',
      })
    }
  })
  return petals
}

const flowers = [
  { id: 'a', petals: peony(1), class: 'peony peony-a' },
  { id: 'b', petals: peony(7), class: 'peony peony-b' },
  { id: 'c', petals: peony(19), class: 'peony peony-c' },
]

/** Falling petals: position across the screen, size, speed and start offset. */
const falling = Array.from({ length: 12 }, (_, i) => ({
  key: i,
  left: `${(i * 37 + 11) % 100}%`,
  size: 10 + ((i * 7) % 9),
  duration: `${16 + ((i * 5) % 12)}s`,
  delay: `${-((i * 3.7) % 24)}s`,
  drift: `${((i % 2 ? 1 : -1) * (20 + ((i * 13) % 60)))}px`,
}))
</script>

<template>
  <div class="floral" aria-hidden="true">
    <svg width="0" height="0" class="absolute">
      <defs>
        <radialGradient id="petal-deep" cx="0.5" cy="0.2" r="0.9">
          <stop offset="0" stop-color="#f5cfda" />
          <stop offset="0.55" stop-color="#d98aa3" />
          <stop offset="1" stop-color="#8e3352" />
        </radialGradient>
        <radialGradient id="petal-mid" cx="0.5" cy="0.2" r="0.9">
          <stop offset="0" stop-color="#f8d9e2" />
          <stop offset="0.6" stop-color="#e3a1b5" />
          <stop offset="1" stop-color="#a5455f" />
        </radialGradient>
        <radialGradient id="petal-light" cx="0.5" cy="0.25" r="0.9">
          <stop offset="0" stop-color="#fbe5ec" />
          <stop offset="0.7" stop-color="#eab3c3" />
          <stop offset="1" stop-color="#b9566f" />
        </radialGradient>
        <radialGradient id="bloom-shade" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0.55" stop-color="#2a0f1c" stop-opacity="0" />
          <stop offset="1" stop-color="#2a0f1c" stop-opacity="0.55" />
        </radialGradient>
      </defs>
    </svg>

    <svg v-for="f in flowers" :key="f.id" :class="f.class" viewBox="-130 -130 260 260">
      <!-- leaves -->
      <path d="M-20 40 C -90 60, -130 120, -125 128 C -80 122, -40 90, -20 40 Z" fill="#2f4d46" />
      <path d="M30 35 C 100 40, 128 95, 126 110 C 80 108, 45 80, 30 35 Z" fill="#26423c" />
      <!-- petals, outer rings first -->
      <ellipse
        v-for="p in f.petals"
        :key="p.key"
        cx="0"
        :cy="p.cy"
        :rx="p.rx"
        :ry="p.ry"
        :fill="p.fill"
        stroke="#6d1f3a"
        stroke-opacity="0.25"
        stroke-width="0.8"
        :transform="`rotate(${p.rotate})`"
      />
      <circle r="78" fill="url(#bloom-shade)" />
    </svg>

    <span
      v-for="p in falling"
      :key="p.key"
      class="petal"
      :style="{ left: p.left, width: `${p.size}px`, height: `${p.size}px`, animationDuration: p.duration, animationDelay: p.delay, '--drift': p.drift }"
    >
      <svg viewBox="0 0 20 20"><path d="M10 1 C 17 4, 19 12, 10 19 C 1 12, 3 4, 10 1 Z" fill="#eaa6bc" /></svg>
    </span>
  </div>
</template>

<style scoped>
.floral {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
  /* Plum at the top, garden teal lower down, with soft pink light. */
  background:
    radial-gradient(60% 45% at 85% 10%, rgb(234 166 188 / 0.14), transparent 70%),
    radial-gradient(50% 40% at 5% 95%, rgb(234 166 188 / 0.1), transparent 70%),
    linear-gradient(170deg, #22161d 0%, #1b1418 45%, #16201f 100%);
}

.peony {
  position: absolute;
  filter: drop-shadow(0 20px 30px rgb(0 0 0 / 0.45));
  animation: sway 14s ease-in-out infinite alternate;
}
/* Big bloom off the top-right corner, a medium one bottom-left, a bud mid-right. */
.peony-a {
  width: 460px;
  top: -110px;
  right: -120px;
  opacity: 0.4;
}
.peony-b {
  width: 360px;
  bottom: -190px;
  left: -190px;
  opacity: 0.3;
  animation-duration: 18s;
}
.peony-c {
  width: 170px;
  top: 52%;
  right: -85px;
  opacity: 0.24;
  animation-duration: 11s;
}
@keyframes sway {
  from {
    transform: rotate(-2deg);
  }
  to {
    transform: rotate(3deg);
  }
}

.petal {
  position: absolute;
  top: -40px;
  opacity: 0.55;
  animation: fall linear infinite;
}
.petal svg {
  display: block;
  width: 100%;
  height: 100%;
}
@keyframes fall {
  from {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(var(--drift), 55vh) rotate(200deg);
  }
  to {
    transform: translate(0, 112vh) rotate(420deg);
  }
}

@media (max-width: 640px) {
  .peony-a {
    width: 300px;
    right: -110px;
  }
  .peony-b {
    width: 260px;
  }
  .peony-c {
    display: none;
  }
}
</style>
