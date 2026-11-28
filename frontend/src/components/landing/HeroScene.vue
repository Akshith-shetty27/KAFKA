<script setup>
/**
 * The landing hero's one 3D element: a slowly turning sphere of points, one per
 * question in the bank, banded and coloured by track. It leans toward the
 * pointer while hovered.
 *
 * Loaded lazily (this file and three.js are a separate chunk, imported after
 * first paint). Cost controls:
 *   - device-pixel-ratio capped at 1.5; antialias off (points don't need it)
 *   - the render loop runs only while the canvas is on screen and the tab is
 *     visible (IntersectionObserver + visibilitychange)
 *   - reduced motion: one still frame, no loop, no pointer tracking
 *   - no WebGL: emits `unavailable` and renders nothing (the panel's grid
 *     texture behind it is the designed fallback)
 * Everything is disposed on unmount.
 */
import { BufferGeometry, Color, Float32BufferAttribute, Group, PerspectiveCamera, Points, PointsMaterial, Scene, WebGLRenderer } from 'three'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { prefersReducedMotion } from '@/motion'

const props = defineProps({
  /** [{ count, color }] — one band of points per track, in order */
  bands: { type: Array, required: true },
})
const emit = defineEmits(['unavailable'])

const host = ref(null)
let renderer, scene, camera, group, geometry, material, frame, observer, resizeObserver
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

/** Points on a sphere (Fibonacci spiral), split into latitude bands by track. */
function buildGeometry() {
  const total = Math.min(2400, props.bands.reduce((n, b) => n + b.count, 0)) || 1
  const positions = new Float32Array(total * 3)
  const colors = new Float32Array(total * 3)
  const golden = Math.PI * (3 - Math.sqrt(5))
  let i = 0
  for (const band of props.bands) {
    const color = new Color(band.color)
    const n = Math.round((band.count / Math.max(1, props.bands.reduce((s, b) => s + b.count, 0))) * total)
    for (let k = 0; k < n && i < total; k++, i++) {
      const y = 1 - (i / (total - 1 || 1)) * 2 // 1 → -1, so bands stack top to bottom
      const r = Math.sqrt(1 - y * y)
      const theta = golden * i
      // Small radial jitter so the shell reads as a cloud, not a wireframe.
      const jitter = 1 + (Math.sin(i * 12.9898) * 43758.5453 % 1) * 0.035
      positions.set([Math.cos(theta) * r * jitter, y * jitter, Math.sin(theta) * r * jitter], i * 3)
      colors.set([color.r, color.g, color.b], i * 3)
    }
  }
  const g = new BufferGeometry()
  g.setAttribute('position', new Float32BufferAttribute(positions.subarray(0, i * 3), 3))
  g.setAttribute('color', new Float32BufferAttribute(colors.subarray(0, i * 3), 3))
  return g
}

function resize() {
  const el = host.value
  if (!el || !renderer) return
  const { clientWidth: w, clientHeight: h } = el
  renderer.setSize(w, h, false)
  camera.aspect = w / Math.max(1, h)
  camera.updateProjectionMatrix()
  renderer.render(scene, camera)
}

function tick(time) {
  frame = requestAnimationFrame(tick)
  const dt = Math.min(64, time - (lastTime || time))
  lastTime = time
  // Slow drift, plus an eased lean toward the pointer.
  group.rotation.y += dt * 0.00008
  pointer.x += (pointer.tx - pointer.x) * 0.05
  pointer.y += (pointer.ty - pointer.y) * 0.05
  group.rotation.x = 0.35 + pointer.y * 0.25
  group.rotation.z = pointer.x * -0.12
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
  camera = new PerspectiveCamera(42, 1, 0.1, 20)
  // Far enough that the whole sphere fits the (tall, narrow) panel with a margin.
  camera.position.set(0, 0, 5)
  geometry = buildGeometry()
  material = new PointsMaterial({ size: 0.034, vertexColors: true, transparent: true, opacity: 0.9, depthWrite: false })
  group = new Group()
  group.add(new Points(geometry, material))
  group.rotation.set(0.35, 0.6, 0)
  scene.add(group)

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
  geometry?.dispose()
  material?.dispose()
  renderer?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div ref="host" class="pointer-events-none absolute inset-0 [&>canvas]:block [&>canvas]:h-full [&>canvas]:w-full" />
</template>
