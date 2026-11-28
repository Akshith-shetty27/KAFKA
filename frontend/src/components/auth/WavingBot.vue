<script setup>
/**
 * The sign-in / register panel's greeter: a speech bubble over KAFKA's robot.
 * The robot is 3D (RobotScene, three.js, loaded lazily and faded in once
 * drawn). Without WebGL the flat SVG robot below stands in — it bobs, blinks
 * and waves with CSS alone. With reduced motion either one stands still,
 * arm raised mid-wave, so it still reads as a greeting.
 */
import { defineAsyncComponent, ref } from 'vue'

defineProps({
  /** What the speech bubble says. A change replays the bubble and the wave. */
  greeting: { type: String, required: true },
  /** Show the speech bubble above the robot. */
  bubble: { type: Boolean, default: true },
})

const RobotScene = defineAsyncComponent(() => import('./RobotScene.vue'))
const ready = ref(false)
const flat = ref(false)
</script>

<template>
  <div class="bot flex flex-col items-center">
    <p v-if="bubble" :key="greeting" class="bot-bubble relative mb-2 max-w-xs px-6 py-4 text-center text-xl leading-snug font-medium">
      {{ greeting }}
    </p>

    <div v-if="!flat" class="relative h-[22rem] w-[20rem] transition-opacity duration-700 xl:h-[25rem] xl:w-[23rem]" :class="ready ? 'opacity-100' : 'opacity-0'">
      <RobotScene :wave-key="greeting" @ready="ready = true" @unavailable="flat = true" />
    </div>

    <svg v-else class="bot-body w-56 xl:w-64" viewBox="0 0 240 270" fill="none" aria-hidden="true">
      <!-- shadow -->
      <ellipse class="bot-shadow" cx="120" cy="256" rx="58" ry="7" />

      <g class="bot-float">
        <!-- antenna -->
        <line x1="120" y1="40" x2="120" y2="18" class="bot-line" stroke-width="4" stroke-linecap="round" />
        <circle cx="120" cy="14" r="7" class="bot-led" />

        <!-- left arm (resting) -->
        <rect x="46" y="150" width="20" height="58" rx="10" class="bot-shell" transform="rotate(12 56 150)" />
        <circle cx="50" cy="212" r="11" class="bot-shell" />

        <!-- body -->
        <rect x="68" y="138" width="104" height="88" rx="24" class="bot-shell" />
        <circle cx="120" cy="170" r="9" class="bot-led bot-core" />
        <rect x="96" y="194" width="48" height="6" rx="3" class="bot-trim" />

        <!-- waving arm: raised up and out past the head, rotating around the shoulder -->
        <g class="bot-arm">
          <rect x="160" y="80" width="20" height="80" rx="10" class="bot-shell" transform="rotate(41 170 156)" />
          <circle cx="221" cy="96" r="13" class="bot-shell" />
        </g>

        <!-- legs -->
        <rect x="88" y="224" width="20" height="26" rx="8" class="bot-shell" />
        <rect x="132" y="224" width="20" height="26" rx="8" class="bot-shell" />

        <!-- neck + head -->
        <rect x="108" y="124" width="24" height="18" rx="6" class="bot-trim" />
        <rect x="56" y="38" width="128" height="94" rx="28" class="bot-shell" />
        <rect x="72" y="54" width="96" height="62" rx="18" class="bot-screen" />
        <!-- face -->
        <g class="bot-eyes">
          <rect x="92" y="70" width="14" height="18" rx="7" class="bot-led" />
          <rect x="134" y="70" width="14" height="18" rx="7" class="bot-led" />
        </g>
        <path d="M106 99 Q120 110 134 99" class="bot-smile" stroke-width="4" stroke-linecap="round" />
        <circle cx="86" cy="100" r="5" class="bot-cheek" />
        <circle cx="154" cy="100" r="5" class="bot-cheek" />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.bot-shell {
  fill: var(--color-ink-850);
  stroke: rgb(255 255 255 / 0.14);
  stroke-width: 2;
}
.bot-trim {
  fill: var(--color-ink-700);
}
.bot-screen {
  fill: #08201d;
  stroke: rgb(34 220 200 / 0.25);
  stroke-width: 1.5;
}
.bot-line {
  stroke: rgb(255 255 255 / 0.3);
}
.bot-led {
  fill: var(--color-accent);
}
.bot-smile {
  stroke: var(--color-accent);
}
.bot-cheek {
  fill: rgb(34 220 200 / 0.25);
}
.bot-shadow {
  fill: rgb(34 220 200 / 0.12);
}
.bot-core {
  filter: drop-shadow(0 0 6px rgb(34 220 200 / 0.8));
}

.bot-bubble {
  background: var(--color-ink-850);
  border: 1px solid rgb(255 255 255 / 0.14);
  border-radius: 18px;
  animation: bot-bubble-in 500ms cubic-bezier(0.2, 0.9, 0.3, 1.3) both;
}
/* the bubble's tail, pointing down at the robot */
.bot-bubble::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  width: 14px;
  height: 14px;
  background: inherit;
  border-right: inherit;
  border-bottom: inherit;
  transform: translateX(-50%) rotate(45deg);
}

/* SVG parts rotate/move around points in the drawing's own coordinates. */
.bot-float,
.bot-arm,
.bot-eyes,
.bot-shadow {
  transform-box: view-box;
}
.bot-float {
  animation: bot-float 3.2s ease-in-out infinite;
}
.bot-shadow {
  transform-origin: 120px 256px;
  animation: bot-shadow 3.2s ease-in-out infinite;
}
.bot-arm {
  transform-origin: 170px 156px; /* the shoulder */
  animation: bot-wave 3.6s ease-in-out infinite;
}
.bot-eyes {
  transform-origin: 120px 79px;
  animation: bot-blink 4.8s infinite;
}

@keyframes bot-bubble-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.92);
  }
}
@keyframes bot-float {
  50% {
    transform: translateY(-6px);
  }
}
@keyframes bot-shadow {
  50% {
    transform: scaleX(0.86);
    opacity: 0.7;
  }
}
/* Three quick waves, then a rest with the arm still raised. */
@keyframes bot-wave {
  0%,
  45%,
  100% {
    transform: rotate(0deg);
  }
  8%,
  24% {
    transform: rotate(-16deg);
  }
  16%,
  32% {
    transform: rotate(10deg);
  }
  38% {
    transform: rotate(-10deg);
  }
}
@keyframes bot-blink {
  0%,
  92%,
  100% {
    transform: scaleY(1);
  }
  95% {
    transform: scaleY(0.1);
  }
}
</style>
