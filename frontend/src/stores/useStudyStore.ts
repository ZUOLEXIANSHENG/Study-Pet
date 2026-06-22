import { defineStore } from 'pinia'
import { api, type StreamEvent } from '../services/api'

type CompanionAction = 'idle' | 'intro' | 'focus' | 'happy' | 'encourage' | 'comfort' | 'nudge' | 'warning'
type CompanionId = 'cafe' | 'tamamo' | 'rice' | 'calstone' | 'staygold'
type ActiveModule = null | 'chat' | 'plan' | 'checkin'
type ChatTurn = { role: 'user' | 'assistant'; content: string }
type PlanItem = { day: number; task: string }
type WeeklyPlanItem = { week: number; goal: string }
type CheckinItem = { subject: string; minutes: number; createdAt: string }
type AppEvent = { id: number; event_type: string; created_at: string; result: Record<string, unknown> }
type InteractiveType = 'mindmap' | 'challenge' | 'simulation' | 'coach_practice'
type InteractiveStep = { id: string; title: string; description: string }
type InteractiveNode = { id: string; label: string; level: number; status: string; children: string[] }
type InteractiveWidget = { id: string; label: string; min: number; max: number; value: number }
type InteractiveActivity = {
  id: string
  type: InteractiveType
  title: string
  objective: string
  source: string
  nodes: InteractiveNode[]
  steps: InteractiveStep[]
  checkpoints: string[]
  completion_rule: string
  pet_action: string
  widgets: InteractiveWidget[]
  status: string
  created_at: string
}

type AgentEnvelope = {
  agent: string
  result: Record<string, unknown>
  confidence: number
}

const companionProfiles: Record<CompanionId, { name: string; greeting: string }> = {
  cafe: { name: 'Cafe', greeting: '欢迎回来。先设置一个学习目标吧，我会陪你一点点推进。' },
  tamamo: { name: 'Tamamo', greeting: '我们先从你的目标开始，一步一步来。' },
  rice: { name: 'Rice', greeting: '不用急，先告诉我你想完成什么。' },
  calstone: { name: 'Calstone', greeting: '先建立计划，再稳定推进。今天也可以很轻地开始。' },
  staygold: { name: 'StayGold', greeting: '准备好了就设定目标，我会陪你执行。' },
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

function mapPetAction(value: string): CompanionAction {
  const mapping: Record<string, CompanionAction> = {
    comfort: 'comfort',
    encourage: 'encourage',
    celebrate: 'happy',
    remind: 'nudge',
    plan: 'intro',
    guide: 'intro',
    focus: 'focus',
    grow: 'happy',
    steady: 'idle',
  }
  return mapping[value] ?? 'idle'
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

    moodMessage: '',
    chatHistory: [] as ChatTurn[],

    goal: '',
    targetScore: 0,
    daysLeft: 30,
    currentLevel: '',
    examType: '',
    planItems: [] as PlanItem[],
    weeklyPlanItems: [] as WeeklyPlanItem[],

    checkinSubject: '',
    checkinMinutes: 0,
    checkins: [] as CheckinItem[],
    streakDays: 0,

    interactiveType: 'mindmap' as InteractiveType,
    interactiveTopic: '',
    interactiveSourceText: '',
    currentActivity: null as InteractiveActivity | null,
    completedInteractiveSteps: [] as string[],
    interactiveHistory: [] as InteractiveActivity[],
    interactiveResult: null as null | Record<string, unknown>,

    generatedImageUrl: '',
    generatedImageError: '',
    ttsAudioUrl: '',
    ttsError: '',
    documentSummary: '',
    documentError: '',
    events: [] as AppEvent[],

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
    interactiveProgress(state) {
      if (!state.currentActivity?.steps.length) return 0
      return Math.round((state.completedInteractiveSteps.length / state.currentActivity.steps.length) * 100)
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
      this.companionMessage = '我在听，正在想怎么陪你把这一步变轻一点。'

      const history = this.chatHistory.slice(-6)
      const assistantTurn: ChatTurn = { role: 'assistant', content: '' }
      this.chatHistory.push({ role: 'user', content: message })
      this.chatHistory.push(assistantTurn)

      try {
        await api.chatStream(
          {
            user_id: this.userId,
            message,
            companion_id: this.companionId,
            history,
          },
          (event) => this.applyChatStreamEvent(event, assistantTurn),
        )
        if (!assistantTurn.content.trim()) {
          assistantTurn.content = '我在。我们先把任务缩小一点，从一个 10 分钟的小动作开始。'
          this.companionMessage = assistantTurn.content
        }
        this.moodMessage = ''
      } catch (error) {
        const fallback = '刚才连接有点不稳定，但我还在。我们先做一个 10 分钟小任务，把状态轻轻拉回来。'
        assistantTurn.content = fallback
        this.companionAction = 'comfort'
        this.companionMessage = fallback
        throw error
      } finally {
        this.loading = false
      }
    },
    applyChatStreamEvent(event: StreamEvent, assistantTurn: ChatTurn) {
      if (event.type === 'thinking') {
        this.companionAction = 'comfort'
        return
      }
      if (event.type === 'text_delta' && event.content) {
        assistantTurn.content += event.content
        this.companionMessage = assistantTurn.content
        return
      }
      if (event.type === 'emotion' && event.value) {
        if (['anxious', 'tired', 'frustrated'].includes(event.value)) this.companionAction = 'comfort'
        if (['steady', 'happy', 'confident'].includes(event.value)) this.companionAction = 'encourage'
        return
      }
      if (event.type === 'pet_action' && event.value) {
        this.companionAction = mapPetAction(event.value)
        return
      }
      if (event.type === 'done') {
        this.lastResult = {
          agent: event.agent ?? 'companion',
          result: event.result ?? {},
          confidence: Number(event.confidence ?? 0),
        }
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
        this.companionMessage = readText(this.lastResult, ['warning'], '计划生成好了，你可以继续按自己的节奏微调。')
      } finally {
        this.loading = false
      }
    },
    async runPlanFromDocument(file: File) {
      this.loading = true
      this.companionAction = 'intro'
      this.documentError = ''
      try {
        this.lastResult = (await api.generatePlanFromDocument(file, {
          user_id: this.userId,
          exam_type: this.examType,
          target_score: this.targetScore,
          days_left: this.daysLeft,
          current_level: this.currentLevel,
        })) as AgentEnvelope
        this.planItems = readPlan(this.lastResult)
        this.weeklyPlanItems = readWeeklyPlan(this.lastResult)
        this.companionMessage = readText(this.lastResult, ['warning'], '已根据资料生成学习计划。')
      } catch (error) {
        this.documentError = error instanceof Error ? error.message : '资料导入失败'
      } finally {
        this.loading = false
      }
    },
    async parseDocument(file: File) {
      this.loading = true
      this.documentError = ''
      try {
        const result = await api.parseDocument(file, this.userId) as { text?: string; word_count?: number }
        this.documentSummary = `${result.text ?? ''}`.slice(0, 240)
        this.companionMessage = `资料已读取，约 ${result.word_count ?? 0} 个词。`
      } catch (error) {
        this.documentError = error instanceof Error ? error.message : '资料解析失败'
      } finally {
        this.loading = false
      }
    },
    async generateInteractiveActivity(type?: InteractiveType) {
      this.loading = true
      this.interactiveType = type ?? this.interactiveType
      this.interactiveResult = null
      const topic = this.interactiveTopic.trim() || this.examType.trim() || this.goal.trim()
      try {
        const activity = await api.generateInteractive({
          user_id: this.userId,
          type: this.interactiveType,
          topic,
          goal: this.goal,
          source_text: this.interactiveSourceText || this.documentSummary,
          plan_items: this.planItems,
        }) as InteractiveActivity
        this.currentActivity = activity
        this.completedInteractiveSteps = []
        this.interactiveHistory.unshift(activity)
        this.companionAction = mapPetAction(activity.pet_action)
        this.companionMessage = `探索舱已准备好：${activity.title}`
      } finally {
        this.loading = false
      }
    },
    toggleInteractiveStep(stepId: string) {
      if (this.completedInteractiveSteps.includes(stepId)) {
        this.completedInteractiveSteps = this.completedInteractiveSteps.filter((id) => id !== stepId)
      } else {
        this.completedInteractiveSteps.push(stepId)
      }
    },
    async completeInteractiveActivity() {
      if (!this.currentActivity) return
      this.loading = true
      try {
        this.interactiveResult = await api.completeInteractive({
          user_id: this.userId,
          activity_id: this.currentActivity.id,
          type: this.currentActivity.type,
          completed_steps: this.completedInteractiveSteps,
        }) as Record<string, unknown>
        this.companionAction = 'happy'
        this.companionMessage = String(this.interactiveResult.message ?? '这次探索已经记录好了。')
        await this.loadEvents()
      } finally {
        this.loading = false
      }
    },
    async generatePetConcept() {
      this.loading = true
      this.generatedImageError = ''
      try {
        const result = await api.generateImage({
          user_id: this.userId,
          prompt: `A premium cute AI study companion avatar inspired by ${this.currentCompanionName}`,
          style: 'premium cute ai companion, Apple x Notion minimal UI mood',
          aspect_ratio: '1:1',
        }) as { image_url?: string; b64_json?: string }
        this.generatedImageUrl = result.image_url || (result.b64_json ? `data:image/png;base64,${result.b64_json}` : '')
        this.companionAction = 'happy'
        this.companionMessage = this.generatedImageUrl ? '新的桌宠概念图生成好了。' : '图片服务返回了结果，但没有图片地址。'
      } catch (error) {
        this.generatedImageError = error instanceof Error ? error.message : '图片生成失败'
        this.companionMessage = '图片服务暂时不可用，可以稍后再试。'
      } finally {
        this.loading = false
      }
    },
    async speakCompanionMessage() {
      this.loading = true
      this.ttsError = ''
      try {
        const result = await api.textToSpeech({
          user_id: this.userId,
          text: this.companionMessage,
        }) as { audio_base64?: string }
        if (this.ttsAudioUrl) URL.revokeObjectURL(this.ttsAudioUrl)
        const bytes = Uint8Array.from(atob(result.audio_base64 ?? ''), (char) => char.charCodeAt(0))
        this.ttsAudioUrl = URL.createObjectURL(new Blob([bytes], { type: 'audio/mpeg' }))
      } catch (error) {
        this.ttsError = error instanceof Error ? error.message : '语音生成失败'
      } finally {
        this.loading = false
      }
    },
    async loadEvents() {
      const result = await api.events(this.userId, 12) as { events?: AppEvent[] }
      this.events = result.events ?? []
    },
    addCheckin() {
      const subject = this.checkinSubject.trim()
      const minutes = Number(this.checkinMinutes)
      if (!subject || !Number.isFinite(minutes) || minutes <= 0) return
      this.checkins.unshift({ subject, minutes, createdAt: new Date().toISOString() })
      this.streakDays = Math.max(1, this.streakDays || 1)
      this.companionAction = 'happy'
      this.companionMessage = `收到，${subject} ${minutes} 分钟已经记下来了。`
      this.checkinSubject = ''
      this.checkinMinutes = 0
    },
  },
})
