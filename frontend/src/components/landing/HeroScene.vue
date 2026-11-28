<script setup>
/**
 * The landing hero's one 3D element: a small planet of questions.
 *   - the globe: one glowing point per question in the bank, banded and coloured
 *     by track; the far side fades into the dark (fog) for depth
 *   - a tilted ring of dust orbiting it, with one bright "satellite" per track
 * The whole system leans toward the pointer while hovered.
 *
 * Loaded lazily (this file and three.js are a separate chunk, imported after
 * first paint). Cost controls:
 *   - device-pixel-ratio capped at 1.5; antialias off (points don't need it)
 *   - the render loop runs only while the canvas is on screen and the tab is
 *     visible (IntersectionObserver + visibilitychange)
 *   - reduced motion: one still frame, no loop, no pointer tracking
 *   - no WebGL: emits `unavailable` and renders nothing (the panel's gradient
 *     sky behind it is the designed fallback)
 * Everything is disposed on unmount.
 */
import {
  AdditiveBlending,
  BufferGeometry,
  CanvasTexture,
  Color,
  Float32BufferAttribute,
  Fog,
  Group,
  PerspectiveCamera,
  Points,
  PointsMaterial,
  Scene,
  WebGLRenderer,
} from 'three'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { prefersReducedMotion } from '@/motion'

const props = defineProps({
  /** [{ count, color }] — one band of points per track, in order */
  bands: { type: Array, required: true },
})
const emit = defineEmits(['unavailable'])

// Layout of the system, in world units.
const GLOBE_R = 1
const RING_INNER = 1.42
const RING_OUTER = 1.78
const FIT_W = RING_OUTER * 1.04 // half-width the camera must fit (the ring's span)
const FIT_H = 1.32 // half-height (globe + the tilted ring's top and bottom)

const host = ref(null)
let renderer, scene, camera, system, globe, ring, satellites, frame, observer, resizeObserver
const disposables = []
let visible = true
let lastTime = 0
const pointer = { x: 0, y: 0, tx: 0, ty: 0 }

function webglAvailable() {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

/** Deterministic pseudo-random in [0, 1), so the scene looks the same every visit. */
function rand(seed) {
  const x = Math.sin(seed * 12.9898) * 43758.5453
  return x - Math.floor(x)
}

/** A soft round sprite, so points read as light rather than squares. */
function dotTexture() {
  const size = 64
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  g.addColorStop(0, 'rgba(255,255,255,1)')
  g.addColorStop(0.35, 'rgba(255,255,255,0.85)')
  g.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.fillStyle = g
  ctx.fillRect(0, 0, size, size)
  const texture = new CanvasTexture(canvas)
  disposables.push(texture)
  return texture
}

function material(options) {
  const m = new PointsMaterial({ transparent: true, depthWrite: false, blending: AdditiveBlending, ...options })
  disposables.push(m)
  return m
}

function points(positions, colors, mat) {
  const g = new BufferGeometry()
  g.setAttribute('position', new Float32BufferAttribute(positions, 3))
  if (colors) g.setAttribute('color', new Float32BufferAttribute(colors, 3))
  disposables.push(g)
  return new Points(g, mat)
}

/** Points on a sphere (Fibonacci spiral), split into latitude bands by track. */
function buildGlobe(map) {
  const sum = props.bands.reduce((n, b) => n + b.count, 0)
  const total = Math.min(2400, sum) || 1
  const positions = []
  const colors = []
  const golden = Math.PI * (3 - Math.sqrt(5))
  let i = 0
  for (const band of props.bands) {
    const color = new Color(band.color)
    const n = Math.round((band.count / Math.max(1, sum)) * total)
    for (let k = 0; k < n && i < total; k++, i++) {
      const y = 1 - (i / (total - 1 || 1)) * 2 // 1 → -1, so bands stack top to bottom
      const r = Math.sqrt(1 - y * y)
      const theta = golden * i
      const jitter = GLOBE_R * (1 + rand(i) * 0.04) // a cloud, not a wireframe
      positions.push(Math.cos(theta) * r * jitter, y * jitter, Math.sin(theta) * r * jitter)
      colors.push(color.r, color.g, color.b)
    }
  }
  return points(positions, colors, material({ map, size: 0.075, vertexColors: true, opacity: 0.95 }))
}

/** A flat ring of dust, denser toward its middle. */
function buildRing(map) {
  const positions = []
  const colors = []
  const inner = new Color('#22dcc8')
  const outer = new Color('#7fd3e6')
  for (let i = 0; i < 900; i++) {
    const t = (rand(i + 1.7) + rand(i + 9.1)) / 2 // triangular: bunches toward the centre line
    const radius = RING_INNER + (RING_OUTER - RING_INNER) * t
    const angle = rand(i + 4.2) * Math.PI * 2
    positions.push(Math.cos(angle) * radius, (rand(i + 6.6) - 0.5) * 0.04, Math.sin(angle) * radius)
    const c = inner.clone().lerp(outer, t)
    const fade = 0.35 + 0.65 * (1 - Math.abs(t - 0.5) * 2) // dimmer at both edges
    colors.push(c.r * fade, c.g * fade, c.b * fade)
  }
  return points(positions, colors, material({ map, size: 0.045, vertexColors: true, opacity: 0.8 }))
}

/** One bright point per track, each on its own inclined orbit. */
function buildSatellites(map) {
  const orbits = props.bands.slice(0, 3).map((band, i) => ({
    radius: [1.6, 1.3, 1.95][i],
    speed: [0.00022, -0.00031, 0.00016][i], // radians per ms
    phase: i * 2.1,
    tilt: [0.25, -0.55, 0.9][i],
    color: new Color(band.color),
  }))
  const colors = orbits.flatMap((o) => [o.color.r, o.color.g, o.color.b])
  const obj = points(new Array(orbits.length * 3).fill(0), colors, material({ map, size: 0.24, vertexColors: true }))
  obj.userData.orbits = orbits
  return obj
}

function placeSatellites(time) {
  const attr = satellites.geometry.getAttribute('position')
  satellites.userData.orbits.forEach((o, i) => {
    const a = o.phase + time * o.speed
    const x = Math.cos(a) * o.radius
    const z = Math.sin(a) * o.radius
    attr.setXYZ(i, x, z * Math.sin(o.tilt), z * Math.cos(o.tilt))
  })
  attr.needsUpdate = true
}

function resize() {
  const el = host.value
  if (!el || !renderer) return
  const { clientWidth: w, clientHeight: h } = el
  renderer.setSize(w, h, false)
  camera.aspect = w / Math.max(1, h)
  // Back the camera off just enough that the ring fits the width and the
  // system fits the height, whatever shape the panel is.
  const halfV = (camera.fov * Math.PI) / 360
  const halfH = Math.atan(Math.tan(halfV) * camera.aspect)
  const distance = Math.max(FIT_H / Math.tan(halfV), FIT_W / Math.tan(halfH)) * 1.06
  camera.position.z = distance
  scene.fog.near = distance - 0.6
  scene.fog.far = distance + 1.9
  camera.updateProjectionMatrix()
  renderer.render(scene, camera)
}

function tick(time) {
  frame = requestAnimationFrame(tick)
  const dt = Math.min(64, time - (lastTime || time))
  lastTime = time
  globe.rotation.y += dt * 0.00008
  ring.rotation.y += dt * 0.00005
  placeSatellites(time)
  // The system leans toward the pointer.
  pointer.x += (pointer.tx - pointer.x) * 0.05
  pointer.y += (pointer.ty - pointer.y) * 0.05
  system.rotation.x = 0.28 + pointer.y * 0.2
  system.rotation.z = -0.32 + pointer.x * -0.1
  renderer.render(scene, camera)
}

function start() {
  if (!frame && visible && !document.hidden) {
    lastTime = 0
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
function onPointer(event) {
  const rect = host.value.getBoundingClientRect()
  pointer.tx = ((event.clientX - rect.left) / rect.width - 0.5) * 2
  pointer.ty = ((event.clientY - rect.top) / rect.height - 0.5) * 2
}
function onLeave() {
  pointer.tx = pointer.ty = 0
}

onMounted(() => {
  if (!webglAvailable()) {
    emit('unavailable')
    return
  }
  const el = host.value
  renderer = new WebGLRenderer({ alpha: true, antialias: false, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1))
  renderer.domElement.setAttribute('aria-hidden', 'true')
  el.appendChild(renderer.domElement)

  scene = new Scene()
  scene.fog = new Fog('#000000', 4, 7) // near/far set in resize()
  camera = new PerspectiveCamera(40, 1, 0.1, 40)

  const map = dotTexture()
  globe = buildGlobe(map)
  ring = buildRing(map)
  satellites = buildSatellites(map)
  placeSatellites(0)

  system = new Group()
  system.add(globe, ring, satellites)
  system.rotation.set(0.28, 0, -0.32)
  globe.rotation.y = 0.6
  scene.add(system)

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(el)
  resize()

  if (prefersReducedMotion()) return // one still frame (rendered by resize)

  observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting
    visible ? start() : stop()
  })
  observer.observe(el)
  document.addEventListener('visibilitychange', onVisibility)
  el.parentElement.addEventListener('pointermove', onPointer)
  el.parentElement.addEventListener('pointerleave', onLeave)
  start()
})

onBeforeUnmount(() => {
  stop()
  observer?.disconnect()
  resizeObserver?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  host.value?.parentElement?.removeEventListener('pointermove', onPointer)
  host.value?.parentElement?.removeEventListener('pointerleave', onLeave)
  disposables.forEach((d) => d.dispose())
  renderer?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div ref="host" class="pointer-events-none absolute inset-0 [&>canvas]:block [&>canvas]:h-full [&>canvas]:w-full" />
</template>
