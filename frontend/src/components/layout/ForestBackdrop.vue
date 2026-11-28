<script setup>
/**
 * The Forest theme's scene, behind the whole signed-in app (after the "Aerion"
 * reference): a dark sky with the sun breaking through on the right and slowly
 * breathing rays, a jagged snow-lit mountain range, mist drifting across it, and a
 * meadow of dandelions and daisies swaying over a pool of light on the moss, with
 * golden pollen rising.
 *
 * SVG + CSS only, drawn in code. A dark scrim keeps the left and middle quiet so
 * text stays readable; with reduced motion the global rule stops the motion.
 */

/** Deterministic pseudo-random, so the meadow grows the same way every visit. */
function rand(seed) {
  const x = Math.sin(seed * 12.9898 + 4.1) * 43758.5453
  return x - Math.floor(x)
}

const GROUND = 900 // bottom of the 1440×900 scene

// Grass blades along the bottom; the ones near the light pool are lit.
const BLADES = Array.from({ length: 240 }, (_, i) => {
  const x = rand(i + 1) * 1440
  const h = 40 + rand(i + 2) * 120
  const lean = (rand(i + 3) - 0.5) * 40
  const lit = Math.abs(x - 860) < 260 && rand(i + 4) > 0.35
  return {
    key: i,
    d: `M${x} ${GROUND} Q${x + lean * 0.4} ${GROUND - h / 2} ${x + lean} ${GROUND - h}`,
    stroke: lit ? '#4f6d36' : '#1f2b19',
    opacity: 0.55 + rand(i + 5) * 0.45,
  }
})

// Flowers: dandelion puffs, daisies and small golden wildflowers on tall stems.
const FLOWERS = Array.from({ length: 26 }, (_, i) => {
  const x = 40 + rand(i + 31) * 1360
  const h = 60 + rand(i + 32) * 120 // stays in the bottom fifth, below the content
  const kind = i % 5 === 0 ? 'puff' : i % 3 === 0 ? 'gold' : 'daisy'
  return {
    key: i,
    x,
    h,
    kind,
    bend: (rand(i + 33) - 0.5) * 30,
    scale: 0.65 + rand(i + 34) * 0.5,
    duration: `${5 + rand(i + 35) * 4}s`,
    delay: `${-rand(i + 36) * 6}s`,
  }
})
const PUFF_RAYS = Array.from({ length: 22 }, (_, i) => (i * 360) / 22)
const DAISY_PETALS = Array.from({ length: 12 }, (_, i) => (i * 360) / 12)

// Pollen and fireflies drifting up through the light.
const POLLEN = Array.from({ length: 28 }, (_, i) => ({
  key: i,
  style: {
    left: `${30 + rand(i + 61) * 68}%`,
    bottom: `${rand(i + 62) * 40}%`,
    width: `${2 + rand(i + 63) * 3}px`,
    height: `${2 + rand(i + 63) * 3}px`,
    animationDuration: `${12 + rand(i + 64) * 14}s, ${2 + rand(i + 65) * 3}s`,
    animationDelay: `${-rand(i + 66) * 20}s, ${-rand(i + 67) * 4}s`,
    '--dx': `${(rand(i + 68) - 0.5) * 120}px`,
  },
}))
</script>

<template>
  <div class="forest" aria-hidden="true">
    <div class="sky" />
    <div class="rays" />

    <svg class="scene" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice">
      <defs>
        <linearGradient id="fr-far" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#363d37" />
          <stop offset="1" stop-color="#121612" />
        </linearGradient>
        <linearGradient id="fr-near" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#1c221d" />
          <stop offset="1" stop-color="#0c0f0c" />
        </linearGradient>
        <radialGradient id="fr-pool" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stop-color="#b9d66f" stop-opacity="0.45" />
          <stop offset="0.5" stop-color="#6f8f3c" stop-opacity="0.18" />
          <stop offset="1" stop-color="#6f8f3c" stop-opacity="0" />
        </radialGradient>
      </defs>

      <!-- far range, main peak catching the sun on its right flank -->
      <polygon
        fill="url(#fr-far)"
        points="420,620 520,560 590,585 660,500 720,530 790,430 850,470 930,360 990,400 1060,250 1110,320 1150,290 1210,380 1270,350 1340,450 1400,420 1440,470 1440,900 420,900"
      />
      <polygon fill="#e4e5da" opacity="0.55" points="1060,250 1110,320 1095,330 1075,300 1062,330 1050,290" />
      <polygon fill="#e4e5da" opacity="0.42" points="1110,320 1150,290 1210,380 1185,372 1160,330 1135,350" />
      <polygon fill="#e4e5da" opacity="0.3" points="930,360 990,400 970,405 950,385 935,400" />
      <!-- nearer, darker ridge -->
      <polygon
        fill="url(#fr-near)"
        points="0,700 120,650 240,690 360,620 470,670 600,600 720,660 840,610 980,680 1120,630 1260,690 1440,640 1440,900 0,900"
      />
      <!-- light pool on the moss -->
      <ellipse cx="860" cy="860" rx="420" ry="90" fill="url(#fr-pool)" />

      <!-- grass -->
      <path v-for="b in BLADES" :key="b.key" :d="b.d" :stroke="b.stroke" :stroke-opacity="b.opacity" stroke-width="2" fill="none" />

      <!-- flowers -->
      <g
        v-for="f in FLOWERS"
        :key="f.key"
        class="flower"
        :style="{ animationDuration: f.duration, animationDelay: f.delay, transformOrigin: `${f.x}px ${GROUND}px` }"
      >
        <path :d="`M${f.x} ${GROUND} Q${f.x + f.bend} ${GROUND - f.h / 2} ${f.x + f.bend * 0.6} ${GROUND - f.h}`" stroke="#2e3d24" stroke-width="2" fill="none" />
        <g :transform="`translate(${f.x + f.bend * 0.6} ${GROUND - f.h}) scale(${f.scale})`">
          <template v-if="f.kind === 'puff'">
            <line v-for="a in PUFF_RAYS" :key="a" x1="0" y1="0" x2="0" y2="-17" stroke="#e9e6da" stroke-opacity="0.55" stroke-width="0.8" :transform="`rotate(${a})`" />
            <circle v-for="a in PUFF_RAYS" :key="`d${a}`" cx="0" cy="-17" r="1.2" fill="#f4f1e6" fill-opacity="0.7" :transform="`rotate(${a})`" />
            <circle r="2.5" fill="#8d8a6e" />
          </template>
          <template v-else-if="f.kind === 'daisy'">
            <ellipse v-for="a in DAISY_PETALS" :key="a" cx="0" cy="-8" rx="2.6" ry="7" fill="#f2efe3" fill-opacity="0.85" :transform="`rotate(${a})`" />
            <circle r="4" fill="#e3b24b" />
          </template>
          <template v-else>
            <circle cx="-4" cy="-2" r="3.2" fill="#e8b84f" />
            <circle cx="3" cy="-5" r="3.6" fill="#f0c860" />
            <circle cx="2" cy="3" r="3" fill="#d9a43f" />
          </template>
        </g>
      </g>
    </svg>

    <div class="mist" />
    <div class="scrim" />
    <span v-for="p in POLLEN" :key="p.key" class="pollen" :style="p.style" />
  </div>
</template>

<style scoped>
.forest {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
  background: #0b0e0b;
}
/* Storm-dark sky with the sun breaking through top-right. */
.sky {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(18% 22% at 88% 20%, rgb(255 236 190 / 0.55), transparent 70%),
    radial-gradient(45% 40% at 85% 22%, rgb(240 200 130 / 0.22), transparent 75%),
    radial-gradient(60% 35% at 30% 10%, rgb(40 46 40 / 0.6), transparent 70%),
    linear-gradient(180deg, #0d100d 0%, #121712 55%, #0b0e0b 100%);
}
/* Sun rays fanning down-left from the sun, slowly breathing and turning. */
.rays {
  position: absolute;
  inset: -20%;
  background: repeating-conic-gradient(from 200deg at 80% 30%, rgb(255 226 160 / 0.09) 0deg 2.5deg, transparent 2.5deg 8deg);
  mask-image: radial-gradient(50% 55% at 80% 30%, #000 0%, rgb(0 0 0 / 0.5) 40%, transparent 75%);
  transform-origin: 80% 30%;
  animation: rays 14s ease-in-out infinite alternate;
}
@keyframes rays {
  from {
    opacity: 0.55;
    transform: rotate(-2deg);
  }
  to {
    opacity: 1;
    transform: rotate(2deg);
  }
}
.scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.flower {
  animation: sway ease-in-out infinite alternate;
}
@keyframes sway {
  from {
    transform: rotate(-2.5deg);
  }
  to {
    transform: rotate(2.5deg);
  }
}
/* A band of mist drifting slowly across the mountains' feet. */
.mist {
  position: absolute;
  left: -30%;
  right: -30%;
  top: 52%;
  height: 22%;
  background: radial-gradient(50% 50% at 50% 50%, rgb(200 205 195 / 0.12), transparent 70%);
  filter: blur(10px);
  animation: mist 40s ease-in-out infinite alternate;
}
@keyframes mist {
  from {
    transform: translateX(-8%);
  }
  to {
    transform: translateX(8%);
  }
}
/* Keeps the reading area (left and middle) calm, like the reference. */
.scrim {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgb(11 14 11 / 0.78) 0%, rgb(11 14 11 / 0.45) 45%, rgb(11 14 11 / 0.1) 80%),
    linear-gradient(180deg, rgb(11 14 11 / 0.35), transparent 40%);
}
.pollen {
  position: absolute;
  border-radius: 9999px;
  background: #f4d27a;
  box-shadow: 0 0 6px 1px rgb(244 210 122 / 0.8);
  animation-name: rise, glimmer;
  animation-timing-function: linear, ease-in-out;
  animation-iteration-count: infinite, infinite;
  animation-direction: normal, alternate;
}
@keyframes rise {
  from {
    transform: translate(0, 0);
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  85% {
    opacity: 1;
  }
  to {
    transform: translate(var(--dx), -55vh);
    opacity: 0;
  }
}
@keyframes glimmer {
  from {
    filter: brightness(0.6);
  }
  to {
    filter: brightness(1.4);
  }
}
</style>
