<template>
  <main class="pet-app" :data-mode="store.selected ? 'home' : 'select'">
    <section class="pet-scene">
      <div v-if="!store.selected" class="picker-strip">
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

      <div class="pet-name">{{ store.currentCompanionName }}</div>

      <CompanionSprite
        class="main-pet"
        :companion-id="store.companionId"
        :action="store.companionAction"
        @select="store.selectCompanion(store.companionId)"
      />

      <button v-if="!store.selected" class="confirm-arrow" type="button" aria-label="确认桌宠" @click="store.confirmCompanion">
        →
      </button>

      <div v-else class="action-bubbles">
        <button type="button" class="action-bubble chat" @click="store.openModule('chat')">要聊聊天吗</button>
        <button type="button" class="action-bubble plan" @click="store.openModule('plan')">帮你制定学习计划</button>
        <button type="button" class="action-bubble checkin" @click="store.openModule('checkin')">今日打卡</button>
      </div>
    </section>

    <section v-if="store.activeModule === 'chat'" class="module-panel chat-panel">
      <header>
        <p>{{ store.currentCompanionName }}</p>
        <button type="button" @click="store.closeModule">×</button>
      </header>
      <div class="chat-log">
        <div v-if="store.chatHistory.length === 0" class="empty-line">{{ store.companionMessage }}</div>
        <div v-for="(turn, index) in store.chatHistory" :key="index" :class="['chat-line', turn.role]">
          {{ turn.content }}
        </div>
      </div>
      <div class="composer">
        <textarea v-model="store.moodMessage" rows="3" placeholder="说说你现在的状态" @keydown.ctrl.enter.prevent="store.runMood" />
        <button type="button" @click="store.runMood" :disabled="store.loading">
          {{ store.loading ? '...' : '发送' }}
        </button>
      </div>
    </section>

    <section v-if="store.activeModule === 'plan'" class="module-panel plan-panel">
      <header>
        <p>学习计划</p>
        <button type="button" @click="store.closeModule">×</button>
      </header>
      <div class="plan-form">
        <input v-model="store.examType" placeholder="考试/科目，比如 高考数学" />
        <input v-model="store.goal" placeholder="目标，比如 30 天提到 85 分" />
        <div class="form-row">
          <input v-model.number="store.targetScore" type="number" min="0" max="750" placeholder="目标分" />
          <input v-model.number="store.daysLeft" type="number" min="1" placeholder="剩余天数" />
        </div>
        <input v-model="store.currentLevel" placeholder="当前水平，比如 中等/薄弱" />
        <button type="button" @click="store.runPlan" :disabled="store.loading">
          {{ store.loading ? '生成中' : '生成计划' }}
        </button>
      </div>
      <div class="plan-result">
        <p class="module-message">{{ store.companionMessage }}</p>
        <div v-for="item in store.weeklyPlanItems" :key="`week-${item.week}`" class="week-item">
          <span>Week {{ item.week }}</span>
          <strong>{{ item.goal }}</strong>
        </div>
        <div v-for="item in store.planItems" :key="item.day" class="plan-item">
          <span>Day {{ item.day }}</span>
          <input v-model="item.task" />
        </div>
        <button type="button" class="plan-refresh" @click="store.runPlan">重新生成</button>
      </div>
    </section>

    <section v-if="store.activeModule === 'checkin'" class="module-panel checkin-panel">
      <header>
        <p>今日打卡</p>
        <button type="button" @click="store.closeModule">×</button>
      </header>
      <div class="checkin-summary">
        <div><span>连续</span><strong>{{ store.streakDays }} 天</strong></div>
        <div><span>今日</span><strong>{{ store.todayStudyMinutes }} 分钟</strong></div>
        <div><span>科目</span><strong>{{ store.todaySubjects.length || 0 }}</strong></div>
      </div>
      <div class="plan-form">
        <input v-model="store.checkinSubject" placeholder="学习科目" />
        <input v-model.number="store.checkinMinutes" type="number" min="1" placeholder="学习时长/分钟" />
        <button type="button" @click="store.addCheckin">记录打卡</button>
      </div>
      <div class="checkin-list">
        <div v-for="(item, index) in store.checkins" :key="index">
          <span>{{ item.subject }}</span>
          <strong>{{ item.minutes }} 分钟</strong>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import CompanionSprite from './components/CompanionSprite.vue'
import { useStudyStore } from './stores/useStudyStore'

const store = useStudyStore()
</script>
