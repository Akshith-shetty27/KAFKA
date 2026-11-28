<script setup>
/**
 * KAFKA's 3D robot for the sign-in / register panel, built from three.js
 * primitives (no model files): a glossy cream hover-bot with a dark glass
 * visor and teal lights.
 *
 * What it does:
 *   - waves (three quick waves, then a pause with the arm still raised),
 *     starting again whenever `waveKey` changes
 *   - floats on a glowing hover ring, blinks, and its antenna and chest pulse
 *   - turns its head toward the pointer anywhere on the page
 *
 * Loaded lazily (its own chunk; three.js is shared with the landing scene).
 * Cost controls: device-pixel-ratio capped at 1.5; renders only while on
 * screen and the tab is visible. Reduced motion: one still frame mid-wave.
 * No WebGL: emits `unavailable` (the parent shows a flat drawing instead).
 * Everything is disposed on unmount.
 */
import {
  ACESFilmicToneMapping,
  AdditiveBlending,
  CanvasTexture,
  CapsuleGeometry,
  CircleGeometry,
  Color,
  CylinderGeometry,
  DirectionalLight,
  Group,
  HemisphereLight,
  Mesh,
  MeshBasicMaterial,
  MeshPhysicalMaterial,
  MeshStandardMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  PointLight,
  Scene,
  SphereGeometry,
  TorusGeometry,
  WebGLRenderer,
} from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { prefersReducedMotion } from '@/motion'

const props = defineProps({
  /** Change it to make the robot start waving again (e.g. a new greeting). */
  waveKey: { type: String, default: '' },
})
const emit = defineEmits(['unavailable', 'ready'])

const ACCENT = '#22dcc8'
const WAVE_MS = 1500 // three waves
const CYCLE_MS = 4600 // wave, then rest with the arm up

const host = ref(null)
let renderer, scene, camera, frame, observer, resizeObserver
let bot, head, eyes, antennaTip, core, hoverRing, floorGlow, rightShoulder, rightElbow, leftShoulder
let visible = true
let reduced = false
let waveStart = 0
let nextBlink = 0
const pointer = { x: 0, y: 0, tx: 0, ty: 0 }

function webglAvailable() {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

// --- materials -------------------------------------------------------------------------
function materials() {
  return {
    shell: new MeshPhysicalMaterial({ color: '#efece3', roughness: 0.32, metalness: 0.05, clearcoat: 0.9, clearcoatRoughness: 0.2 }),
    joint: new MeshStandardMaterial({ color: '#1d2222', roughness: 0.45, metalness: 0.55 }),
    visor: new MeshPhysicalMaterial({ color: '#04110f', roughness: 0.12, metalness: 0.3, clearcoat: 1, clearcoatRoughness: 0.05 }),
    glow: new MeshBasicMaterial({ color: ACCENT, toneMapped: false }),
    cheek: new MeshBasicMaterial({ color: ACCENT, transparent: true, opacity: 0.35, toneMapped: false }),
  }
}

/** A soft radial light pool for under the robot. */
function glowTexture() {
  const size = 128
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  g.addColorStop(0, 'rgba(34,220,200,0.55)')
  g.addColorStop(0.4, 'rgba(34,220,200,0.18)')
  g.addColorStop(1, 'rgba(34,220,200,0)')
  ctx.fillStyle = g
  ctx.fillRect(0, 0, size, size)
  return new CanvasTexture(canvas)
}

function mesh(geometry, material, [x = 0, y = 0, z = 0] = [], [rx = 0, ry = 0, rz = 0] = []) {
  const m = new Mesh(geometry, material)
  m.position.set(x, y, z)
  m.rotation.set(rx, ry, rz)
  return m
}

/** Shoulder → upper arm → elbow → forearm → hand. Returns the shoulder and elbow pivots. */
function buildArm(side, mat) {
  const shoulder = new Group()
  shoulder.position.set(side * 0.74, 0.28, 0)
  shoulder.add(mesh(new SphereGeometry(0.17, 24, 16), mat.joint))
  shoulder.add(mesh(new CapsuleGeometry(0.115, 0.26, 6, 16), mat.shell, [0, -0.25, 0]))
  const elbow = new Group()
  elbow.position.set(0, -0.46, 0)
  elbow.add(mesh(new SphereGeometry(0.12, 20, 14), mat.joint))
  elbow.add(mesh(new CapsuleGeometry(0.105, 0.22, 6, 16), mat.shell, [0, -0.22, 0]))
  elbow.add(mesh(new SphereGeometry(0.15, 24, 16), mat.shell, [0, -0.46, 0]))
  shoulder.add(elbow)
  return { shoulder, elbow }
}

function build() {
  const mat = materials()
  bot = new Group()

  // Body, chest screen and pulsing core.
  bot.add(mesh(new RoundedBoxGeometry(1.25, 1.12, 0.95, 5, 0.34), mat.shell))
  bot.add(mesh(new RoundedBoxGeometry(0.72, 0.5, 0.08, 3, 0.04), mat.visor, [0, 0.06, 0.47]))
  core = mesh(new CircleGeometry(0.1, 32), mat.glow, [0, 0.06, 0.515])
  bot.add(core)
  bot.add(mesh(new CircleGeometry(0.035, 16), mat.cheek, [-0.22, 0.06, 0.515]))
  bot.add(mesh(new CircleGeometry(0.035, 16), mat.cheek, [0.22, 0.06, 0.515]))

  // Hover base with a glowing ring.
  bot.add(mesh(new CylinderGeometry(0.42, 0.28, 0.2, 40), mat.joint, [0, -0.66, 0]))
  hoverRing = mesh(new TorusGeometry(0.31, 0.035, 12, 48), mat.glow, [0, -0.77, 0], [Math.PI / 2, 0, 0])
  bot.add(hoverRing)

  // Neck and head (the head group pivots at the neck so it can look around).
  bot.add(mesh(new CylinderGeometry(0.16, 0.2, 0.2, 24), mat.joint, [0, 0.64, 0]))
  head = new Group()
  head.position.set(0, 0.72, 0)
  head.add(mesh(new RoundedBoxGeometry(1.5, 1.1, 1.15, 5, 0.4), mat.shell, [0, 0.52, 0]))
  head.add(mesh(new RoundedBoxGeometry(1.22, 0.76, 0.12, 4, 0.07), mat.visor, [0, 0.52, 0.54]))
  eyes = new Group()
  eyes.position.set(0, 0.58, 0.61)
  eyes.add(mesh(new CapsuleGeometry(0.07, 0.13, 6, 16), mat.glow, [-0.25, 0, 0]))
  eyes.add(mesh(new CapsuleGeometry(0.07, 0.13, 6, 16), mat.glow, [0.25, 0, 0]))
  head.add(eyes)
  // Smile: the lower half of a thin torus.
  head.add(mesh(new TorusGeometry(0.13, 0.026, 10, 32, Math.PI), mat.glow, [0, 0.42, 0.61], [0, 0, Math.PI]))
  head.add(mesh(new CircleGeometry(0.055, 20), mat.cheek, [-0.42, 0.38, 0.605]))
  head.add(mesh(new CircleGeometry(0.055, 20), mat.cheek, [0.42, 0.38, 0.605]))
  // Ears with lit rings.
  for (const side of [-1, 1]) {
    head.add(mesh(new CylinderGeometry(0.17, 0.17, 0.12, 32), mat.joint, [side * 0.78, 0.52, 0], [0, 0, Math.PI / 2]))
    head.add(mesh(new TorusGeometry(0.1, 0.022, 8, 32), mat.glow, [side * 0.845, 0.52, 0], [0, Math.PI / 2, 0]))
  }
  // Antenna.
  head.add(mesh(new CylinderGeometry(0.03, 0.04, 0.34, 12), mat.shell, [0, 1.22, 0]))
  antennaTip = mesh(new SphereGeometry(0.085, 20, 14), mat.glow, [0, 1.42, 0])
  head.add(antennaTip)
  bot.add(head)

  // Arms: the right one is raised to wave, the left hangs relaxed.
  const right = buildArm(1, mat)
  rightShoulder = right.shoulder
  rightElbow = right.elbow
  rightShoulder.rotation.z = 2.45 // points up and out
  const left = buildArm(-1, mat)
  leftShoulder = left.shoulder
  leftShoulder.rotation.z = -0.18
  left.elbow.rotation.z = -0.15
  bot.add(rightShoulder, leftShoulder)

  bot.rotation.y = -0.18
  scene.add(bot)

  // A soft pool of teal light on the "floor" below it.
  const texture = glowTexture()
  floorGlow = mesh(
    new PlaneGeometry(2.4, 2.4),
    new MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false, blending: AdditiveBlending, toneMapped: false }),
    [0, -1.3, 0],
    [-Math.PI / 2, 0, 0],
  )
  scene.add(floorGlow)

  // Lights: hemisphere base, a warm-white key, a teal rim from behind, a cool fill.
  scene.add(new HemisphereLight('#e6fffb', '#0b1f1c', 0.9))
  const key = new DirectionalLight('#ffffff', 2.4)
  key.position.set(3, 4, 5)
  scene.add(key)
  const fill = new DirectionalLight('#9fe8e0', 0.6)
  fill.position.set(-4, 1, 3)
  scene.add(fill)
  const rim = new PointLight(new Color(ACCENT), 30, 12)
  rim.position.set(-2.2, 2.4, -2.5)
  scene.add(rim)
}

// --- animation ---------------------------------------------------------------------------
function pose(time) {
  // Float, with the light pool shrinking as the robot rises.
  const bob = Math.sin(time * 0.0019) * 0.08
  bot.position.y = bob
  floorGlow.scale.setScalar(1 - bob * 1.5)
  floorGlow.material.opacity = 0.85 - bob * 2

  // Wave: three quick swings of the forearm, then rest with the arm up.
  const t = (time - waveStart) % CYCLE_MS
  const waving = t < WAVE_MS
  const target = waving ? Math.sin((t / WAVE_MS) * Math.PI * 6) * 0.55 : 0.12
  rightElbow.rotation.z += (target - rightElbow.rotation.z) * (waving ? 0.5 : 0.08)
  rightShoulder.rotation.z = 2.45 + (waving ? Math.sin((t / WAVE_MS) * Math.PI * 6) * 0.06 : 0)
  leftShoulder.rotation.z = -0.18 + Math.sin(time * 0.0019 + 1) * 0.04

  // Head and body follow the pointer; a little idle drift when it's still.
  pointer.x += (pointer.tx - pointer.x) * 0.06
  pointer.y += (pointer.ty - pointer.y) * 0.06
  head.rotation.y = pointer.x * 0.55
  head.rotation.x = pointer.y * 0.22
  head.rotation.z = Math.sin(time * 0.0012) * 0.03
  bot.rotation.y = -0.18 + pointer.x * 0.2

  // Blink every few seconds; pulse the antenna and chest lights.
  if (!nextBlink) nextBlink = time + 2500
  const blinking = time > nextBlink && time < nextBlink + 130
  if (time > nextBlink + 130) nextBlink = time + 2800 + Math.random() * 2400
  eyes.scale.y = blinking ? 0.12 : 1
  const pulse = 1 + Math.sin(time * 0.004) * 0.15
  antennaTip.scale.setScalar(pulse)
  core.scale.setScalar(pulse)
  hoverRing.scale.setScalar(1 + Math.sin(time * 0.006) * 0.04)
}

function render(time) {
  pose(time)
  renderer.render(scene, camera)
}

function tick(time) {
  frame = requestAnimationFrame(tick)
  if (!waveStart) waveStart = time
  render(time)
}

function start() {
  if (!frame && visible && !document.hidden && !reduced) frame = requestAnimationFrame(tick)
}
function stop() {
  if (frame) cancelAnimationFrame(frame)
  frame = null
}
function onVisibility() {
  document.hidden ? stop() : start()
}
// Look toward the pointer anywhere on the page, relative to where the robot is.
function onPointer(event) {
  const rect = host.value.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height * 0.35
  pointer.tx = Math.max(-1, Math.min(1, (event.clientX - cx) / (window.innerWidth / 2)))
  pointer.ty = Math.max(-1, Math.min(1, (event.clientY - cy) / (window.innerHeight / 2)))
}

function resize() {
  const el = host.value
  if (!el || !renderer) return
  const { clientWidth: w, clientHeight: h } = el
  renderer.setSize(w, h, false)
  camera.aspect = w / Math.max(1, h)
  camera.updateProjectionMatrix()
  if (reduced || !frame) render(performance.now())
}

// A new greeting starts a new wave.
watch(
  () => props.waveKey,
  () => {
    waveStart = performance.now()
  },
)

onMounted(() => {
  if (!webglAvailable()) {
    emit('unavailable')
    return
  }
  reduced = prefersReducedMotion()
  const el = host.value
  renderer = new WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1))
  renderer.toneMapping = ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.05
  renderer.domElement.setAttribute('aria-hidden', 'true')
  el.appendChild(renderer.domElement)

  scene = new Scene()
  camera = new PerspectiveCamera(30, 1, 0.1, 50)
  camera.position.set(0, 0.7, 8)
  camera.lookAt(0, 0.45, 0)
  build()

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(el)
  // Reduced motion: one still frame, mid-wave (arm up, hand tilted).
  if (reduced) rightElbow.rotation.z = 0.3
  resize()
  emit('ready')
  if (reduced) return

  observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting
    visible ? start() : stop()
  })
  observer.observe(el)
  document.addEventListener('visibilitychange', onVisibility)
  window.addEventListener('pointermove', onPointer, { passive: true })
  start()
})

onBeforeUnmount(() => {
  stop()
  observer?.disconnect()
  resizeObserver?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  window.removeEventListener('pointermove', onPointer)
  scene?.traverse((obj) => {
    obj.geometry?.dispose()
    if (obj.material) {
      obj.material.map?.dispose()
      obj.material.dispose()
    }
  })
  renderer?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div ref="host" class="pointer-events-none absolute inset-0 [&>canvas]:block [&>canvas]:h-full [&>canvas]:w-full" />
</template>
