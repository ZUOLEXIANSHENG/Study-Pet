<template>
  <button class="study-pet-avatar" type="button" aria-label="Talk with StudyPet" @click="$emit('chat')">
    <span class="avatar-aura avatar-aura-one" />
    <span class="avatar-aura avatar-aura-two" />
    <span class="avatar-particle particle-one" />
    <span class="avatar-particle particle-two" />
    <span class="avatar-particle particle-three" />

    <svg viewBox="0 0 420 420" role="img" aria-labelledby="pet-title" class="avatar-svg">
      <title id="pet-title">StudyPet AI companion</title>
      <defs>
        <linearGradient id="petBody" x1="112" x2="310" y1="88" y2="330" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#EEF2FF" />
          <stop offset="0.48" stop-color="#FFFFFF" />
          <stop offset="1" stop-color="#C7D2FE" />
        </linearGradient>
        <linearGradient id="petAccent" x1="134" x2="286" y1="122" y2="278" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#818CF8" />
          <stop offset="1" stop-color="#6366F1" />
        </linearGradient>
        <filter id="petShadow" x="-20%" y="-20%" width="140%" height="150%">
          <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#6366F1" flood-opacity="0.18" />
          <feDropShadow dx="0" dy="34" stdDeviation="24" flood-color="#475569" flood-opacity="0.12" />
        </filter>
      </defs>

      <g filter="url(#petShadow)">
        <path class="ear-left" d="M136 132C124 85 150 58 187 92L171 145Z" fill="#E0E7FF" />
        <path class="ear-right" d="M285 132C297 85 271 58 234 92L250 145Z" fill="#E0E7FF" />
        <path d="M121 184C121 117 160 79 211 79C262 79 300 117 300 184V244C300 302 264 338 211 338C158 338 121 302 121 244V184Z" fill="url(#petBody)" />
        <path d="M151 198C151 155 176 130 211 130C246 130 271 155 271 198V236C271 278 246 303 211 303C176 303 151 278 151 236V198Z" fill="rgba(255,255,255,0.86)" />
        <path d="M172 165C184 151 200 144 211 144C222 144 238 151 250 165C236 158 222 154 211 154C200 154 186 158 172 165Z" fill="#C7D2FE" opacity="0.72" />
        <path class="visor" d="M158 202C158 177 178 160 211 160C244 160 264 177 264 202C264 227 244 244 211 244C178 244 158 227 158 202Z" fill="url(#petAccent)" />
        <circle class="eye eye-left" cx="193" cy="201" r="9" fill="white" />
        <circle class="eye eye-right" cx="229" cy="201" r="9" fill="white" />
        <path d="M198 225C205 231 217 231 224 225" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" />
        <path d="M125 237C93 244 82 276 106 293C122 304 141 291 144 263Z" fill="#F8FAFC" />
        <path d="M296 237C328 244 339 276 315 293C299 304 280 291 277 263Z" fill="#F8FAFC" />
        <path d="M178 296C190 306 232 306 244 296" fill="none" stroke="#C7D2FE" stroke-width="9" stroke-linecap="round" />
      </g>

      <path class="orbit-line" d="M94 221C124 141 185 107 260 125C331 142 357 209 319 265C285 314 211 328 150 299" fill="none" stroke="#A5B4FC" stroke-width="4" stroke-linecap="round" stroke-dasharray="8 18" />
      <circle class="orbit-dot" cx="326" cy="193" r="10" fill="#6366F1" />
    </svg>

    <span class="avatar-platform">
      <span class="platform-glow" />
    </span>
  </button>
</template>

<script setup lang="ts">
defineEmits<{
  chat: []
}>()
</script>
