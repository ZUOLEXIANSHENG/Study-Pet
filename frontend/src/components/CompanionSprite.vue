<template>
  <button class="pet-stage" type="button" :aria-label="`选择 ${companionId}`" @click="$emit('select')">
    <canvas ref="canvasRef" :width="frameWidth" :height="frameHeight" />
    <div class="pet-shadow" />
  </button>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type CompanionAction = 'idle' | 'intro' | 'focus' | 'happy' | 'encourage' | 'comfort' | 'nudge' | 'warning'
type CompanionId = 'cafe' | 'tamamo' | 'rice' | 'calstone' | 'staygold'

const props = defineProps<{
  companionId: CompanionId
  action: CompanionAction
}>()

defineEmits<{
  select: []
}>()

const characterMeta: Record<CompanionId, { frameWidth: number; frameHeight: number; base: string }> = {
  cafe: { frameWidth: 325, frameHeight: 325, base: '/assets/companion/cafe' },
  tamamo: { frameWidth: 300, frameHeight: 300, base: '/assets/companion/tamamo' },
  rice: { frameWidth: 300, frameHeight: 350, base: '/assets/companion/rice' },
  calstone: { frameWidth: 300, frameHeight: 325, base: '/assets/companion/calstone' },
  staygold: { frameWidth: 300, frameHeight: 300, base: '/assets/companion/staygold' },
}

const animationDefs: Record<
  CompanionAction,
  { file: Record<CompanionId, string>; frames: Record<CompanionId, number>; fps: number }
> = {
  idle: {
    file: { cafe: 'idle.png', tamamo: 'idle.png', rice: 'idle.png', calstone: 'idle.png', staygold: 'idle.png' },
    frames: { cafe: 60, tamamo: 340, rice: 340, calstone: 60, staygold: 340 },
    fps: 18,
  },
  intro: {
    file: { cafe: 'intro.png', tamamo: 'intro.png', rice: 'intro.png', calstone: 'intro.png', staygold: 'intro.png' },
    frames: { cafe: 100, tamamo: 50, rice: 50, calstone: 50, staygold: 40 },
    fps: 22,
  },
  focus: {
    file: { cafe: 'runIdle.png', tamamo: 'runIdle.png', rice: 'wIdle.png', calstone: 'runIdle.png', staygold: 'runIdle.png' },
    frames: { cafe: 60, tamamo: 70, rice: 100, calstone: 120, staygold: 50 },
    fps: 20,
  },
  happy: {
    file: { cafe: 'emote1.png', tamamo: 'emote1.png', rice: 'emote1.png', calstone: 'emote1.png', staygold: 'emote1.png' },
    frames: { cafe: 41, tamamo: 41, rice: 155, calstone: 42, staygold: 60 },
    fps: 18,
  },
  encourage: {
    file: { cafe: 'emote4.png', tamamo: 'emote4.png', rice: 'click.png', calstone: 'emote4.png', staygold: 'emote4.png' },
    frames: { cafe: 42, tamamo: 42, rice: 117, calstone: 130, staygold: 45 },
    fps: 18,
  },
  comfort: {
    file: { cafe: 'emote2.png', tamamo: 'emote2.png', rice: 'hover.png', calstone: 'hover.png', staygold: 'hover.png' },
    frames: { cafe: 35, tamamo: 35, rice: 40, calstone: 120, staygold: 60 },
    fps: 16,
  },
  nudge: {
    file: { cafe: 'click.png', tamamo: 'click.png', rice: 'click.png', calstone: 'click.png', staygold: 'click.png' },
    frames: { cafe: 111, tamamo: 113, rice: 117, calstone: 109, staygold: 35 },
    fps: 24,
  },
  warning: {
    file: { cafe: 'sleep.png', tamamo: 'sleep.png', rice: 'sleep.png', calstone: 'sleep.png', staygold: 'sleep.png' },
    frames: { cafe: 50, tamamo: 50, rice: 255, calstone: 255, staygold: 50 },
    fps: 16,
  },
}

const canvasRef = ref<HTMLCanvasElement | null>(null)
const image = new Image()
const loadedFrames = ref(1)
const loadedColumns = ref(1)
let raf = 0
let start = 0
let loaded = false

const meta = computed(() => characterMeta[props.companionId])
const config = computed(() => {
  const animation = animationDefs[props.action]
  return {
    src: `${meta.value.base}/${animation.file[props.companionId]}`,
    frames: animation.frames[props.companionId],
    fps: animation.fps,
    frameWidth: meta.value.frameWidth,
    frameHeight: meta.value.frameHeight,
  }
})
const frameWidth = computed(() => config.value.frameWidth)
const frameHeight = computed(() => config.value.frameHeight)

function render(timestamp: number) {
  const canvas = canvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!canvas || !ctx || !loaded) {
    raf = requestAnimationFrame(render)
    return
  }

  if (!start) start = timestamp
  const frameW = config.value.frameWidth
  const frameH = config.value.frameHeight
  const columns = loadedColumns.value
  const frames = Math.max(1, loadedFrames.value)
  const elapsed = (timestamp - start) / 1000
  const frame = Math.floor(elapsed * config.value.fps) % frames
  const sx = (frame % columns) * frameW
  const sy = Math.floor(frame / columns) * frameH

  ctx.clearRect(0, 0, frameW, frameH)
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(image, sx, sy, frameW, frameH, 0, 0, frameW, frameH)
  raf = requestAnimationFrame(render)
}

function loadSprite() {
  loaded = false
  start = 0
  loadedFrames.value = 1
  loadedColumns.value = 1
  image.onload = () => {
    const sheetColumns = Math.max(1, Math.floor(image.naturalWidth / config.value.frameWidth))
    const sheetRows = Math.max(1, Math.floor(image.naturalHeight / config.value.frameHeight))
    loadedColumns.value = sheetColumns
    loadedFrames.value = Math.min(config.value.frames, sheetColumns * sheetRows)
    loaded = true
  }
  image.src = config.value.src
}

watch(() => [props.action, props.companionId], loadSprite)

onMounted(() => {
  loadSprite()
  raf = requestAnimationFrame(render)
})

onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>
