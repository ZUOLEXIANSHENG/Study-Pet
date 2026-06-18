<template>
  <main class="studypet-shell">
    <div class="ambient ambient-one" />
    <div class="ambient ambient-two" />
    <div class="ambient ambient-three" />

    <header class="topbar glass-card">
      <button class="brand" type="button" @click="activePage = 'home'" aria-label="Open StudyPet home">
        <span class="brand-glyph">S</span>
        <span>StudyPet</span>
      </button>

      <div class="daily-greeting">
        <strong>Good Afternoon, Xiaoming</strong>
        <span>Today is another day of growth.</span>
      </div>

      <div class="topbar-actions">
        <button class="bell-button" type="button" aria-label="Notifications">
          <span class="bell-icon" />
        </button>
        <div class="level-chip">
          <span>Lv. 12</span>
          <i><b /></i>
        </div>
        <div class="user-avatar" aria-label="User avatar">XM</div>
      </div>
    </header>

    <nav class="page-tabs" aria-label="StudyPet pages">
      <button
        v-for="item in navItems"
        :key="item.id"
        type="button"
        :class="{ active: activePage === item.id }"
        @click="activePage = item.id"
      >
        {{ item.label }}
      </button>
    </nav>

    <section v-if="activePage === 'home'" class="page home-page">
      <section class="hero-grid">
        <aside class="hero-left">
          <div class="speech-bubble glass-card">
            <span class="eyebrow">StudyPet says</span>
            <p>You have studied for 12 consecutive days. Keep going. I believe in you.</p>
          </div>

          <div class="pet-info-card glass-card">
            <div class="card-title-row">
              <span class="eyebrow">Companion growth</span>
              <strong>Level 12</strong>
            </div>
            <div class="metric-stack">
              <div>
                <span>EXP</span>
                <strong>2,480 / 3,000</strong>
              </div>
              <div class="mini-progress"><i style="width: 82%" /></div>
              <div>
                <span>Growth status</span>
                <strong>Focused and warm</strong>
              </div>
              <div>
                <span>Next unlock</span>
                <strong>Learning Analysis · 18%</strong>
              </div>
            </div>
          </div>
        </aside>

        <section class="pet-hero" aria-label="StudyPet companion stage">
          <div class="hero-light" />
          <div class="floating-reward reward-one">+50 EXP</div>
          <div class="floating-reward reward-two">+10 Motivation</div>
          <div class="floating-reward reward-three">+1 Streak</div>
          <StudyPetAvatar @chat="activePage = 'home'" />
        </section>

        <aside class="chat-panel glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">AI Chat</span>
              <h2>Talk with StudyPet</h2>
            </div>
            <span class="online-dot" />
          </div>
          <div class="chat-list">
            <p>How was your study today?</p>
            <p>What made you proud today?</p>
            <p>What challenge did you encounter?</p>
          </div>
          <div class="chat-input">
            <input v-model="store.moodMessage" placeholder="Talk with StudyPet..." @keydown.enter.prevent="store.runMood" />
            <button type="button" @click="store.runMood" :disabled="store.loading">Send</button>
          </div>
        </aside>
      </section>

      <section class="bottom-grid">
        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">Today</span>
              <h2>Study Plan</h2>
            </div>
            <strong>67%</strong>
          </div>
          <div class="task-list">
            <label v-for="task in todayTasks" :key="task.name">
              <input type="checkbox" :checked="task.done" />
              <span>{{ task.name }}</span>
              <small>{{ task.time }}</small>
            </label>
          </div>
          <div class="soft-progress"><i style="width: 67%" /></div>
          <button class="soft-button" type="button" @click="activePage = 'planning'">Generate New AI Plan</button>
        </article>

        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">Overview</span>
              <h2>Learning Today</h2>
            </div>
            <span class="pulse-chip">On track</span>
          </div>
          <div class="overview-metrics">
            <div><span>Study Duration</span><strong>2h 35m</strong></div>
            <div><span>Tasks Completed</span><strong>6 / 9</strong></div>
            <div><span>Current Streak</span><strong>12 days</strong></div>
          </div>
          <div class="weekly-line" aria-label="Weekly trend">
            <i v-for="height in weeklyTrend" :key="height" :style="{ height: `${height}%` }" />
          </div>
          <button class="primary-button" type="button" @click="activePage = 'checkin'">Complete Today's Check-in</button>
        </article>

        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">Calendar</span>
              <h2>Study Rhythm</h2>
            </div>
            <strong>12 day streak</strong>
          </div>
          <div class="heatmap" aria-label="Monthly study intensity">
            <span v-for="(cell, index) in heatmapCells" :key="index" :data-level="cell" />
          </div>
          <p class="muted-copy">Purple intensity shows your study energy across this month.</p>
        </article>
      </section>
    </section>

    <section v-else-if="activePage === 'planning'" class="page planning-page">
      <aside class="side-rail glass-card">
        <span class="eyebrow">Roadmap</span>
        <h2>Personal growth plan</h2>
        <p>Build a calm weekly rhythm that adapts to your exam date, weak subjects, and real available time.</p>
        <div class="rail-stat"><span>Weekly focus</span><strong>8.5 h</strong></div>
        <div class="rail-stat"><span>Risk level</span><strong>Low</strong></div>
      </aside>

      <section class="roadmap glass-card">
        <div class="section-heading">
          <span class="eyebrow">Weekly Study Roadmap</span>
          <h1>Your next seven days</h1>
        </div>
        <div class="timeline-board">
          <article v-for="day in weekPlan" :key="day.day" class="day-column">
            <h3>{{ day.day }}</h3>
            <div
              v-for="task in day.tasks"
              :key="task.title"
              class="roadmap-task"
              draggable="true"
            >
              <strong>{{ task.title }}</strong>
              <span>{{ task.meta }}</span>
            </div>
          </article>
        </div>
      </section>

      <aside class="planner-assistant glass-card">
        <span class="eyebrow">AI Planner</span>
        <h2>Generate a personalized plan</h2>
        <label><span>Grade</span><input v-model="planner.grade" placeholder="Senior 3" /></label>
        <label><span>Exam Date</span><input v-model="planner.examDate" type="date" /></label>
        <label><span>Target Score</span><input v-model="planner.targetScore" placeholder="620" /></label>
        <label><span>Daily Available Time</span><input v-model="planner.availableTime" placeholder="2.5 hours" /></label>
        <label><span>Weak Subjects</span><input v-model="planner.weakSubjects" placeholder="Math, Physics" /></label>
        <button class="primary-button" type="button" @click="store.runPlan">Generate Personalized Plan</button>
      </aside>
    </section>

    <section v-else-if="activePage === 'checkin'" class="page checkin-page">
      <section class="streak-hero glass-card">
        <span class="eyebrow">Current Study Streak</span>
        <h1>12 Days</h1>
        <p>Small promises kept daily become the life you are building.</p>
      </section>

      <section class="checkin-center">
        <StudyPetAvatar @chat="activePage = 'growth'" />
        <button class="checkin-button" type="button" @click="completeCheckin">
          <span>Complete Today's Check-in</span>
        </button>
        <div v-if="showCelebration" class="celebration-layer">
          <span>+50 EXP</span>
          <span>+10 Motivation</span>
          <span>+1 Streak</span>
        </div>
      </section>

      <aside class="checkin-calendar glass-card">
        <span class="eyebrow">Calendar</span>
        <h2>June rhythm</h2>
        <div class="heatmap large">
          <span v-for="(cell, index) in heatmapCells" :key="`large-${index}`" :data-level="cell" />
        </div>
      </aside>

      <section class="stats-strip">
        <article class="glass-card"><span>Total Study Hours</span><strong>86.5</strong></article>
        <article class="glass-card"><span>Completed Tasks</span><strong>142</strong></article>
        <article class="glass-card"><span>Weekly Progress</span><strong>78%</strong></article>
        <article class="glass-card"><span>Monthly Progress</span><strong>64%</strong></article>
      </section>
    </section>

    <section v-else class="page growth-page">
      <aside class="achievement-panel glass-card">
        <span class="eyebrow">Achievements</span>
        <h2>Built with you</h2>
        <div v-for="item in achievements" :key="item.title" class="achievement-item">
          <span>{{ item.icon }}</span>
          <div><strong>{{ item.title }}</strong><small>{{ item.meta }}</small></div>
        </div>
      </aside>

      <section class="growth-center glass-card">
        <span class="eyebrow">My Learning Journey</span>
        <h1>StudyPet is growing with you</h1>
        <StudyPetAvatar @chat="activePage = 'home'" />
        <div class="evolution-card">
          <span>Current Evolution Stage</span>
          <strong>Focused Companion · Level 12</strong>
          <div class="soft-progress"><i style="width: 82%" /></div>
        </div>
      </section>

      <aside class="abilities-panel glass-card">
        <span class="eyebrow">Unlocked Abilities</span>
        <h2>Companion skills</h2>
        <div v-for="ability in abilities" :key="ability.title" class="ability-item" :class="{ locked: ability.locked }">
          <strong>{{ ability.title }}</strong>
          <span>{{ ability.meta }}</span>
        </div>
      </aside>

      <section class="growth-timeline glass-card">
        <span class="eyebrow">Growth Timeline</span>
        <div class="milestone-row">
          <div v-for="milestone in milestones" :key="milestone.level" class="milestone">
            <span>{{ milestone.level }}</span>
            <strong>{{ milestone.title }}</strong>
            <small>{{ milestone.reward }}</small>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import StudyPetAvatar from './components/StudyPetAvatar.vue'
import { useStudyStore } from './stores/useStudyStore'

type PageId = 'home' | 'planning' | 'checkin' | 'growth'

const store = useStudyStore()
const activePage = ref<PageId>('home')
const showCelebration = ref(false)

const navItems: Array<{ id: PageId; label: string }> = [
  { id: 'home', label: 'Today' },
  { id: 'planning', label: 'Planning' },
  { id: 'checkin', label: 'Check-in' },
  { id: 'growth', label: 'Growth' },
]

const planner = reactive({
  grade: 'Senior 3',
  examDate: '2026-07-18',
  targetScore: '620',
  availableTime: '2.5 hours',
  weakSubjects: 'Mathematics, Physics',
})

const todayTasks = [
  { name: 'Mathematics Review', time: '30 min', done: true },
  { name: 'English Reading', time: '20 min', done: true },
  { name: 'Physics Practice', time: '40 min', done: false },
]

const weeklyTrend = [42, 64, 58, 76, 72, 88, 66]
const heatmapCells = [0, 1, 2, 3, 1, 0, 2, 4, 3, 2, 1, 0, 3, 4, 4, 2, 1, 3, 2, 0, 1, 4, 3, 2, 2, 1, 3, 4, 2, 1, 0, 3, 2, 4, 1]

const weekPlan = [
  { day: 'Monday', tasks: [{ title: 'Math concept review', meta: '45 min · algebra' }, { title: 'English reading', meta: '20 min · habit' }] },
  { day: 'Tuesday', tasks: [{ title: 'Physics practice', meta: '40 min · weak point' }] },
  { day: 'Wednesday', tasks: [{ title: 'Mistake reflection', meta: '30 min · calm review' }, { title: 'Vocabulary loop', meta: '15 min' }] },
  { day: 'Thursday', tasks: [{ title: 'Mock section', meta: '60 min · timed' }] },
  { day: 'Friday', tasks: [{ title: 'Formula recall', meta: '25 min' }, { title: 'Reading summary', meta: '20 min' }] },
  { day: 'Saturday', tasks: [{ title: 'Full practice set', meta: '90 min · deep work' }] },
  { day: 'Sunday', tasks: [{ title: 'Weekly reset', meta: '30 min · plan next week' }] },
]

const achievements = [
  { icon: '12', title: 'Study Streak', meta: '12 days in a row' },
  { icon: '28', title: 'Completed Plans', meta: '28 plans finished' },
  { icon: '6', title: 'Growth Badges', meta: '6 milestones unlocked' },
]

const abilities = [
  { title: 'Learning Assistant', meta: 'Unlocked · asks better questions', locked: false },
  { title: 'Study Reminder', meta: 'Unlocked · gentle nudges', locked: false },
  { title: 'Learning Analysis', meta: 'Unlocks at Level 14', locked: true },
  { title: 'Future Unlocks', meta: 'Deeper reports and rituals', locked: true },
]

const milestones = [
  { level: 'Lv. 1', title: 'First Promise', reward: '+10 EXP' },
  { level: 'Lv. 6', title: 'Steady Rhythm', reward: 'Reminder voice' },
  { level: 'Lv. 12', title: 'Focused Companion', reward: 'Growth aura' },
  { level: 'Lv. 14', title: 'Insight Partner', reward: 'Analysis unlock' },
]

function completeCheckin() {
  store.addCheckin()
  showCelebration.value = true
  window.setTimeout(() => {
    showCelebration.value = false
  }, 1800)
}
</script>
