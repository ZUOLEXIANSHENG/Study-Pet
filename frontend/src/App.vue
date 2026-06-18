<template>
  <main class="pet-app" :data-mode="store.selected ? 'dashboard' : 'select'">
    <div class="studio-glow studio-glow-a" />
    <div class="studio-glow studio-glow-b" />

    <section class="pet-scene" aria-labelledby="app-title">
      <div class="brand-mark">
        <span class="brand-orbit" aria-hidden="true" />
        <div>
          <h1 id="app-title">StudyPet</h1>
          <p>{{ store.selected ? store.currentCompanionName : 'Choose your companion' }}</p>
        </div>
      </div>

      <div v-if="!store.selected" class="picker-strip" aria-label="选择桌宠">
        <button
          v-for="companion in store.companions"
          :key="companion.id"
          type="button"
          :class="{ active: store.companionId === companion.id }"
          @click="store.selectCompanion(companion.id)"
        >
          {{ companion.name }}
        </button>
      </div>

      <button v-else class="reselect-button" type="button" @click="handleReselect">
        Reselect pet
      </button>

      <div class="pet-stage-shell">
        <div class="stage-ring stage-ring-one" />
        <div class="stage-ring stage-ring-two" />
        <div class="pet-message" :class="{ visible: store.selected || store.activeModule === 'chat' }">
          {{ store.companionMessage }}
        </div>
        <CompanionSprite
          class="main-pet"
          :companion-id="store.companionId"
          :action="store.companionAction"
          @select="handlePetTap"
        />
      </div>

      <button v-if="!store.selected" class="confirm-arrow" type="button" aria-label="确认桌宠" @click="store.confirmCompanion">
        <span aria-hidden="true">›</span>
      </button>

      <nav v-else class="glass-dock" aria-label="StudyPet modules">
        <button type="button" :class="{ active: store.activeModule === 'chat' }" @click="store.openModule('chat')">
          <span class="dock-icon chat-icon" aria-hidden="true" />
          <span>AI Pet Chat</span>
        </button>
        <button type="button" :class="{ active: store.activeModule === 'plan' }" @click="store.openModule('plan')">
          <span class="dock-icon plan-icon" aria-hidden="true" />
          <span>Study Planner</span>
        </button>
        <button type="button" :class="{ active: store.activeModule === 'checkin' }" @click="store.openModule('checkin')">
          <span class="dock-icon focus-icon" aria-hidden="true" />
          <span>Focus Tracker</span>
        </button>
      </nav>
    </section>

    <aside class="chat-sheet glass-panel" :class="{ open: store.activeModule === 'chat' }" aria-label="AI Pet Chat">
      <header class="panel-header">
        <div>
          <p>AI Pet Chat</p>
          <span>{{ store.currentCompanionName }}</span>
        </div>
        <button type="button" class="icon-button" aria-label="关闭聊天" @click="store.closeModule">×</button>
      </header>

      <div class="chat-log">
        <div v-if="store.chatHistory.length === 0" class="empty-line">{{ store.companionMessage }}</div>
        <div v-for="(turn, index) in store.chatHistory" :key="index" :class="['chat-line', turn.role]">
          {{ turn.content }}
        </div>
      </div>

      <div class="composer">
        <label for="mood-message">Message</label>
        <textarea id="mood-message" v-model="store.moodMessage" rows="3" placeholder="说说你现在的状态" @keydown.ctrl.enter.prevent="store.runMood" />
        <button type="button" @click="store.runMood" :disabled="store.loading">
          {{ store.loading ? 'Sending' : 'Send' }}
        </button>
      </div>
    </aside>

    <aside class="planner-drawer glass-panel" :class="{ open: store.activeModule === 'plan' }" aria-label="Study Planner">
      <header class="panel-header">
        <div>
          <p>Study Planner</p>
          <span>Daily tasks and weekly rhythm</span>
        </div>
        <button type="button" class="icon-button" aria-label="关闭计划" @click="store.closeModule">×</button>
      </header>

      <form class="plan-form" @submit.prevent="store.runPlan">
        <label>
          <span>考试/科目</span>
          <input v-model="store.examType" placeholder="高考数学" />
        </label>
        <label>
          <span>目标</span>
          <input v-model="store.goal" placeholder="30 天提到 85 分" />
        </label>
        <div class="form-row">
          <label>
            <span>目标分</span>
            <input v-model.number="store.targetScore" type="number" min="0" max="750" />
          </label>
          <label>
            <span>剩余天数</span>
            <input v-model.number="store.daysLeft" type="number" min="1" />
          </label>
        </div>
        <label>
          <span>当前水平</span>
          <input v-model="store.currentLevel" placeholder="中等/薄弱" />
        </label>
        <button type="submit" class="primary-action" :disabled="store.loading">
          {{ store.loading ? 'Generating' : 'Generate plan' }}
        </button>
      </form>

      <div class="weekly-progress" aria-label="Weekly Progress">
        <div class="progress-copy">
          <span>Weekly Progress</span>
          <strong>{{ weeklyProgress }}%</strong>
        </div>
        <div class="progress-track">
          <i :style="{ width: `${weeklyProgress}%` }" />
        </div>
      </div>

      <div class="timeline">
        <div v-for="item in visiblePlanItems" :key="item.day" class="timeline-item">
          <label class="task-check">
            <input type="checkbox" />
            <span />
          </label>
          <div>
            <small>Day {{ item.day }}</small>
            <input v-model="item.task" aria-label="编辑每日任务" />
          </div>
        </div>
      </div>

      <div v-if="store.weeklyPlanItems.length" class="week-strip">
        <div v-for="item in store.weeklyPlanItems" :key="`week-${item.week}`">
          <span>Week {{ item.week }}</span>
          <strong>{{ item.goal }}</strong>
        </div>
      </div>
    </aside>

    <aside class="focus-overlay glass-panel" :class="{ open: store.activeModule === 'checkin' }" aria-label="Focus Tracker">
      <header class="panel-header">
        <div>
          <p>Focus Tracker</p>
          <span>Check-in stays local</span>
        </div>
        <button type="button" class="icon-button" aria-label="关闭打卡" @click="store.closeModule">×</button>
      </header>

      <div class="timer-orb" :style="{ '--timer-progress': timerProgress }">
        <div>
          <span>{{ timerLabel }}</span>
          <small>{{ timerRunning ? 'Focus session' : 'Ready to focus' }}</small>
        </div>
      </div>

      <div class="timer-controls">
        <button type="button" @click="toggleTimer">{{ timerRunning ? 'Pause' : 'Start' }}</button>
        <button type="button" @click="resetTimer">Reset</button>
      </div>

      <div class="focus-stats">
        <div>
          <span class="stat-icon flame-icon" aria-hidden="true" />
          <small>Streak</small>
          <strong>{{ store.streakDays }} days</strong>
        </div>
        <div>
          <span class="stat-icon pulse-icon" aria-hidden="true" />
          <small>Today</small>
          <strong>{{ store.todayStudyMinutes }} min</strong>
        </div>
      </div>

      <form class="checkin-form" @submit.prevent="store.addCheckin">
        <label>
          <span>科目</span>
          <input v-model="store.checkinSubject" placeholder="数学" />
        </label>
        <label>
          <span>时长/分钟</span>
          <input v-model.number="store.checkinMinutes" type="number" min="1" />
        </label>
        <button type="submit" class="primary-action">Record check-in</button>
      </form>

      <div class="checkin-list">
        <div v-for="(item, index) in store.checkins" :key="index">
          <span>{{ item.subject }}</span>
          <strong>{{ item.minutes }} 分钟</strong>
        </div>
      </div>
    </aside>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import CompanionSprite from './components/CompanionSprite.vue'
import { useStudyStore } from './stores/useStudyStore'

const store = useStudyStore()
const focusMinutes = 25
const remainingSeconds = ref(focusMinutes * 60)
const timerRunning = ref(false)
let timerId = 0

const visiblePlanItems = computed(() => {
  if (store.planItems.length) return store.planItems.slice(0, 7)
  return Array.from({ length: 5 }, (_, index) => ({
    day: index + 1,
    task: ['诊断当前基础', '整理核心概念', '完成专项练习', '订正易错题', '轻量复盘'][index],
  }))
})

const weeklyProgress = computed(() => {
  if (!store.planItems.length) return 18
  const capped = Math.min(store.planItems.length, 7)
  return Math.round((capped / 7) * 100)
})

const timerLabel = computed(() => {
  const minutes = Math.floor(remainingSeconds.value / 60)
  const seconds = remainingSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const timerProgress = computed(() => `${Math.round(((focusMinutes * 60 - remainingSeconds.value) / (focusMinutes * 60)) * 100)}%`)

function handlePetTap() {
  if (!store.selected) {
    store.selectCompanion(store.companionId)
    return
  }
  store.openModule('chat')
}

function handleReselect() {
  timerRunning.value = false
  window.clearInterval(timerId)
  store.reselectCompanion()
}

function toggleTimer() {
  timerRunning.value = !timerRunning.value
  store.companionAction = timerRunning.value ? 'focus' : 'idle'
  if (!timerRunning.value) return
  window.clearInterval(timerId)
  timerId = window.setInterval(() => {
    if (remainingSeconds.value <= 1) {
      remainingSeconds.value = 0
      timerRunning.value = false
      window.clearInterval(timerId)
      store.companionAction = 'happy'
      return
    }
    remainingSeconds.value -= 1
  }, 1000)
}

function resetTimer() {
  timerRunning.value = false
  remainingSeconds.value = focusMinutes * 60
  window.clearInterval(timerId)
  store.companionAction = store.activeModule === 'checkin' ? 'focus' : 'idle'
}

onBeforeUnmount(() => window.clearInterval(timerId))
</script>
