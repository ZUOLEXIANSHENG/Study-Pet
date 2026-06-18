import { defineStore } from 'pinia'
import { api } from '../services/api'

type CompanionAction = 'idle' | 'intro' | 'focus' | 'happy' | 'encourage' | 'comfort' | 'nudge' | 'warning'
type CompanionId = 'cafe' | 'tamamo' | 'rice' | 'calstone' | 'staygold'
type ActiveModule = null | 'chat' | 'plan' | 'checkin'
type ChatTurn = { role: 'user' | 'assistant'; content: string }
type PlanItem = { day: number; task: string }
type WeeklyPlanItem = { week: number; goal: string }
type CheckinItem = { subject: string; minutes: number; createdAt: string }

type AgentEnvelope = {
  agent: string
  result: Record<string, unknown>
  confidence: number
}

const companionProfiles: Record<CompanionId, { name: string; greeting: string }> = {
  cafe: { name: 'Cafe', greeting: '我在这里，先慢慢来。' },
  tamamo: { name: 'Tamamo', greeting: '今天也一起往前冲一点。' },
  rice: { name: 'Rice', greeting: '不用急，我们先把第一步做好。' },
  calstone: { name: 'Calstone', greeting: '节奏交给我，我们稳住。' },
  staygold: { name: 'StayGold', greeting: '先行动一小步，状态会跟上。' },
}

function readText(result: unknown, keys: string[], fallback: string) {
  const envelope = result as AgentEnvelope
  for (const key of keys) {
    const value = envelope?.result?.[key]
    if (typeof value === 'string' && value.trim()) return value
  }
  return fallback
}

function readPlan(result: unknown): PlanItem[] {
  const envelope = result as AgentEnvelope
  const plan = envelope?.result?.plan
  if (!Array.isArray(plan)) return []
  return plan
    .map((item) => {
      const raw = item as Record<string, unknown>
      return { day: Number(raw.day), task: String(raw.task ?? '') }
    })
    .filter((item) => Number.isFinite(item.day) && item.task)
}

function readWeeklyPlan(result: unknown): WeeklyPlanItem[] {
  const envelope = result as AgentEnvelope
  const plan = envelope?.result?.weekly_plan
  if (!Array.isArray(plan)) return []
  return plan
    .map((item) => {
      const raw = item as Record<string, unknown>
      return { week: Number(raw.week), goal: String(raw.goal ?? '') }
    })
    .filter((item) => Number.isFinite(item.week) && item.goal)
}

export const useStudyStore = defineStore('study', {
  state: () => ({
    userId: 'demo',
    selected: false,
    activeModule: null as ActiveModule,
    companionId: 'cafe' as CompanionId,
    companionAction: 'idle' as CompanionAction,
    companionMessage: companionProfiles.cafe.greeting,
    companions: [
      { id: 'cafe' as CompanionId, name: 'Cafe' },
      { id: 'tamamo' as CompanionId, name: 'Tamamo' },
      { id: 'rice' as CompanionId, name: 'Rice' },
      { id: 'calstone' as CompanionId, name: 'Calstone' },
      { id: 'staygold' as CompanionId, name: 'StayGold' },
    ],

    moodMessage: '我今天有点焦虑，学不进去',
    chatHistory: [] as ChatTurn[],

    goal: '期末数学 85 分以上',
    targetScore: 85,
    daysLeft: 30,
    currentLevel: '中等',
    examType: '高考数学',
    planItems: [] as PlanItem[],
    weeklyPlanItems: [] as WeeklyPlanItem[],

    checkinSubject: '数学',
    checkinMinutes: 45,
    checkins: [] as CheckinItem[],
    streakDays: 0,

    lastResult: null as null | AgentEnvelope,
    loading: false,
  }),
  getters: {
    currentCompanionName(state) {
      return companionProfiles[state.companionId].name
    },
    todayStudyMinutes(state) {
      return state.checkins.reduce((sum, item) => sum + item.minutes, 0)
    },
    todaySubjects(state) {
      return [...new Set(state.checkins.map((item) => item.subject))]
    },
  },
  actions: {
    selectCompanion(id: CompanionId) {
      this.companionId = id
      this.companionAction = 'idle'
      this.companionMessage = companionProfiles[id].greeting
      this.chatHistory = []
    },
    confirmCompanion() {
      this.selected = true
      this.companionAction = 'happy'
      this.companionMessage = companionProfiles[this.companionId].greeting
    },
    reselectCompanion() {
      this.selected = false
      this.activeModule = null
      this.companionAction = 'idle'
      this.companionMessage = companionProfiles[this.companionId].greeting
    },
    openModule(module: Exclude<ActiveModule, null>) {
      this.activeModule = module
      if (module === 'chat') this.companionAction = 'comfort'
      if (module === 'plan') this.companionAction = 'intro'
      if (module === 'checkin') this.companionAction = 'focus'
    },
    closeModule() {
      this.activeModule = null
      this.companionAction = 'idle'
    },
    async runMood() {
      const message = this.moodMessage.trim()
      if (!message) return
      this.loading = true
      this.companionAction = 'comfort'
      try {
        const history = this.chatHistory.slice(-6)
        this.chatHistory.push({ role: 'user', content: message })
        this.lastResult = (await api.moodCheck({
          user_id: this.userId,
          message,
          companion_id: this.companionId,
          history,
        })) as AgentEnvelope
        const reply = readText(this.lastResult, ['reply'], '我在，我们先把任务缩小一点。')
        this.companionMessage = reply
        this.chatHistory.push({ role: 'assistant', content: reply })
        this.moodMessage = ''
      } finally {
        this.loading = false
      }
    },
    async runPlan() {
      this.loading = true
      this.companionAction = 'intro'
      try {
        this.lastResult = (await api.generatePlan({
          user_id: this.userId,
          goal: this.goal,
          exam_type: this.examType,
          target_score: this.targetScore,
          days_left: this.daysLeft,
          current_level: this.currentLevel,
        })) as AgentEnvelope
        this.planItems = readPlan(this.lastResult)
        this.weeklyPlanItems = readWeeklyPlan(this.lastResult)
        this.companionMessage = readText(this.lastResult, ['warning'], '计划生成好了，可以直接改成你舒服的节奏。')
      } finally {
        this.loading = false
      }
    },
    addCheckin() {
      const subject = this.checkinSubject.trim()
      const minutes = Number(this.checkinMinutes)
      if (!subject || !Number.isFinite(minutes) || minutes <= 0) return
      this.checkins.unshift({ subject, minutes, createdAt: new Date().toISOString() })
      this.streakDays = Math.max(1, this.streakDays || 1)
      this.companionAction = 'happy'
      this.companionMessage = `收到，${subject} ${minutes} 分钟已经记下来了。`
    },
  },
})
