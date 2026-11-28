<script setup>
/**
 * The Space theme's sky, behind the whole signed-in app: a live starfield on a
 * canvas.
 *   - ~320 stars in three depth layers drift slowly (near ones faster, so it
 *     feels like gliding through space) and lean with the pointer (parallax)
 *   - every star twinkles on its own rhythm; a few bright ones flare with a
 *     four-point sparkle
 *   - a shooting star streaks across every few seconds
 *   - faint teal and violet nebulae breathe underneath (CSS)
 *
 * Cost controls: device-pixel-ratio capped at 1.5, one canvas, the loop pauses
 * while the tab is hidden. Reduced motion: one still frame, no shooting stars.
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { prefersReducedMotion } from '@/motion'

const canvas = ref(null)
let ctx, frame, width, height, dpr
let stars = []
let shooting = []
let nextShot = 0
let last = 0
let still = false // reduced motion: one frame, redrawn on resize
const pointer = { x: 0, y: 0, tx: 0, ty: 0 }

// Star colours: mostly white, some pale teal and blue, the odd warm one.
const TINTS = ['255,252,242', '255,252,242', '255,252,242', '200,246,240', '196,214,255', '255,226,190']
const LAYERS = [
  { count: 220, size: [0.5, 1.0], speed: 0.004, alpha: [0.35, 0.75], parallax: 6 }, // far
  { count: 140, size: [0.8, 1.4], speed: 0.009, alpha: [0.5, 0.9], parallax: 14 }, // middle
  { count: 55, size: [1.1, 2.0], speed: 0.018, alpha: [0.7, 1], parallax: 26 }, // near
]

const between = ([a, b]) => a + Math.random() * (b - a)

function makeStars() {
  stars = []
  // Scale the count with screen area so small screens aren't crowded.
  const density = Math.min(1.2, Math.max(0.45, (width * height) / (1440 * 900)))
  LAYERS.forEach((layer, depth) => {
    for (let i = 0; i < Math.round(layer.count * density); i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: between(layer.size),
        a: between(layer.alpha),
        tint: TINTS[Math.floor(Math.random() * TINTS.length)],
        twinkle: 0.6 + Math.random() * 2.2, // radians per second
        phase: Math.random() * Math.PI * 2,
        speed: layer.speed,
        parallax: layer.parallax,
        // A few near stars get the four-point sparkle.
        sparkle: depth === 2 && Math.random() < 0.45,
      })
    }
  })
}

function resize() {
  const el = canvas.value
  if (!el) return
  dpr = Math.min(1.5, window.devicePixelRatio || 1)
  width = window.innerWidth
  height = window.innerHeight
  el.width = Math.round(width * dpr)
  el.height = Math.round(height * dpr)
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  makeStars()
}

function launchShootingStar() {
  // Start along the top or right edge, streak down-left.
  const fromTop = Math.random() < 0.6
  const x = fromTop ? width * (0.3 + Math.random() * 0.7) : width + 20
  const y = fromTop ? -20 : height * Math.random() * 0.5
  const angle = Math.PI * (0.72 + Math.random() * 0.12) // down and to the left
  const speed = 650 + Math.random() * 350 // px per second — slow enough to catch
  shooting.push({ x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed, life: 0, ttl: 1.3 + Math.random() * 0.6, length: 200 + Math.random() * 140 })
}

function drawStar(s, t, ox, oy) {
  const glow = 0.55 + 0.45 * Math.sin(s.phase + t * s.twinkle)
  const alpha = s.a * glow
  const x = s.x + ox * s.parallax
  const y = s.y + oy * s.parallax
  ctx.fillStyle = `rgba(${s.tint},${alpha})`
  ctx.beginPath()
  ctx.arc(x, y, s.r, 0, Math.PI * 2)
  ctx.fill()
  if (s.sparkle && glow > 0.8) {
    // Four-point flare, strongest at the peak of the twinkle.
    const len = s.r * 7 * (glow - 0.8) * 5
    ctx.strokeStyle = `rgba(${s.tint},${alpha * 0.6})`
    ctx.lineWidth = 0.6
    ctx.beginPath()
    ctx.moveTo(x - len, y)
    ctx.lineTo(x + len, y)
    ctx.moveTo(x, y - len)
    ctx.lineTo(x, y + len)
    ctx.stroke()
    const halo = ctx.createRadialGradient(x, y, 0, x, y, s.r * 5)
    halo.addColorStop(0, `rgba(${s.tint},${alpha * 0.5})`)
    halo.addColorStop(1, `rgba(${s.tint},0)`)
    ctx.fillStyle = halo
    ctx.beginPath()
    ctx.arc(x, y, s.r * 5, 0, Math.PI * 2)
    ctx.fill()
  }
}

function drawShootingStar(s) {
  const p = s.life / s.ttl
  const fade = p < 0.15 ? p / 0.15 : 1 - (p - 0.15) / 0.85 // quick in, long fade out
  const mag = Math.hypot(s.vx, s.vy)
  const tx = s.x - (s.vx / mag) * s.length
  const ty = s.y - (s.vy / mag) * s.length
  const tail = ctx.createLinearGradient(s.x, s.y, tx, ty)
  tail.addColorStop(0, `rgba(255,252,242,${0.9 * fade})`)
  tail.addColorStop(0.25, `rgba(160,240,230,${0.6 * fade})`)
  tail.addColorStop(1, 'rgba(160,240,230,0)')
  ctx.strokeStyle = tail
  ctx.lineWidth = 2.2
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.moveTo(s.x, s.y)
  ctx.lineTo(tx, ty)
  ctx.stroke()
  const head = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, 9)
  head.addColorStop(0, `rgba(255,255,255,${fade})`)
  head.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.fillStyle = head
  ctx.beginPath()
  ctx.arc(s.x, s.y, 9, 0, Math.PI * 2)
  ctx.fill()
}

function render(time, dt) {
  const t = time / 1000
  ctx.clearRect(0, 0, width, height)
  pointer.x += (pointer.tx - pointer.x) * 0.04
  pointer.y += (pointer.ty - pointer.y) * 0.04
  for (const s of stars) {
    // Drift left and slightly up; wrap around the edges.
    s.x -= s.speed * dt * 60
    s.y -= s.speed * dt * 12
    if (s.x < -10) s.x = width + 10
    if (s.y < -10) s.y = height + 10
    drawStar(s, t, pointer.x, pointer.y)
  }
  if (time > nextShot) {
    launchShootingStar()
    nextShot = time + 2500 + Math.random() * 4500
  }
  shooting = shooting.filter((s) => s.life < s.ttl)
  for (const s of shooting) {
    s.life += dt
    s.x += s.vx * dt
    s.y += s.vy * dt
    drawShootingStar(s)
  }
}

function tick(time) {
  frame = requestAnimationFrame(tick)
  const dt = Math.min(0.05, (time - (last || time)) / 1000)
  last = time
  render(time, dt)
}
function start() {
  if (!frame && !document.hidden) {
    last = 0
    frame = requestAnimationFrame(tick)
  }
}
function stop() {
  if (frame) cancelAnimationFrame(frame)
  frame = null
}
function onVisibility() {
  document.hidden ? stop() : start()
}
function drawStill() {
  ctx.clearRect(0, 0, width, height)
  for (const s of stars) drawStar(s, 0, 0, 0)
}
function onResize() {
  resize()
  if (still) drawStill()
}
function onPointer(event) {
  pointer.tx = (event.clientX / width - 0.5) * -1
  pointer.ty = (event.clientY / height - 0.5) * -1
}

onMounted(() => {
  ctx = canvas.value.getContext('2d')
  resize()
  window.addEventListener('resize', onResize)
  if (prefersReducedMotion()) {
    still = true
    drawStill() // a still sky; no drift, no shooting stars
    return
  }
  nextShot = performance.now() + 1500 // the first one comes quickly
  window.addEventListener('pointermove', onPointer, { passive: true })
  document.addEventListener('visibilitychange', onVisibility)
  start()
})

onBeforeUnmount(() => {
  stop()
  window.removeEventListener('resize', onResize)
  window.removeEventListener('pointermove', onPointer)
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <div class="space" aria-hidden="true">
    <div class="nebula" />
    <canvas ref="canvas" class="sky" />
  </div>
</template>

<style scoped>
.space {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}
/* Faint teal and violet nebulae, slowly breathing and drifting. */
.nebula {
  position: absolute;
  inset: -10%;
  background:
    radial-gradient(35% 30% at 78% 22%, rgb(34 220 200 / 0.07), transparent 70%),
    radial-gradient(40% 35% at 18% 75%, rgb(140 110 230 / 0.07), transparent 70%),
    radial-gradient(30% 25% at 55% 50%, rgb(127 211 230 / 0.04), transparent 70%);
  animation: nebula 30s ease-in-out infinite alternate;
}
@keyframes nebula {
  from {
    transform: translate(-2%, 1%) scale(1);
    opacity: 0.7;
  }
  to {
    transform: translate(2%, -1%) scale(1.06);
    opacity: 1;
  }
}
.sky {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
</style>
