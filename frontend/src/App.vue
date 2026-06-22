<template>
  <main class="studypet-shell">
    <div class="ambient ambient-one" />
    <div class="ambient ambient-two" />
    <div class="ambient ambient-three" />

    <header class="topbar glass-card">
      <button class="brand" type="button" @click="activePage = 'home'" aria-label="打开首页">
        <span class="brand-glyph">学</span>
        <span>学习搭子</span>
      </button>

      <div class="daily-greeting">
        <strong>欢迎回来</strong>
        <span>先设置你的目标，StudyPet 会陪你一点点推进。</span>
      </div>

      <div class="topbar-actions">
        <button class="bell-button" type="button" aria-label="通知">
          <span class="bell-icon" />
        </button>
        <div class="level-chip">
          <span>待成长</span>
          <i><b :style="{ width: store.checkins.length ? '12%' : '0%' }" /></i>
        </div>
        <div class="user-avatar" aria-label="用户头像">我</div>
      </div>
    </header>

    <nav class="page-tabs" aria-label="页面导航">
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
            <span class="eyebrow">StudyPet 说</span>
            <p>{{ store.companionMessage }}</p>
          </div>

          <div class="pet-info-card glass-card">
            <div class="card-title-row">
              <span class="eyebrow">伙伴成长</span>
              <strong>待开始</strong>
            </div>
            <div class="metric-stack">
              <div>
                <span>经验值</span>
                <strong>暂无记录</strong>
              </div>
              <div class="mini-progress"><i :style="{ width: store.checkins.length ? '12%' : '0%' }" /></div>
              <div>
                <span>成长状态</span>
                <strong>{{ store.checkins.length ? '正在积累' : '等待你的第一次打卡' }}</strong>
              </div>
              <div>
                <span>下一步</span>
                <strong>{{ store.planItems.length ? '完成今日任务' : '先生成学习计划' }}</strong>
              </div>
            </div>
          </div>
        </aside>

        <section class="pet-hero" aria-label="StudyPet 舞台">
          <div class="hero-light" />
          <div v-if="store.checkins.length" class="floating-reward reward-one">+{{ store.checkins.length }} 次记录</div>
          <StudyPetAvatar @chat="activePage = 'home'" />
        </section>

        <aside class="chat-panel glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">AI 对话</span>
              <h2>和 StudyPet 聊聊</h2>
            </div>
            <span class="online-dot" />
          </div>
          <div class="chat-list">
            <template v-if="store.chatHistory.length">
              <p
                v-for="(turn, index) in store.chatHistory"
                :key="`${turn.role}-${index}`"
                :class="`chat-turn ${turn.role}`"
              >
                {{ turn.content || 'StudyPet 正在思考...' }}
              </p>
            </template>
            <template v-else>
              <p>你可以告诉我：今天想学什么？</p>
              <p>也可以说：我有点焦虑，学不进去。</p>
              <p>我会根据你的状态给出陪伴式回应。</p>
            </template>
          </div>
          <div class="chat-input">
            <input v-model="store.moodMessage" placeholder="和 StudyPet 说点什么..." @keydown.enter.prevent="store.runMood" />
            <button type="button" @click="store.runMood" :disabled="store.loading">发送</button>
          </div>
        </aside>
      </section>

      <section class="bottom-grid">
        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">今日</span>
              <h2>学习计划</h2>
            </div>
            <strong>{{ store.planItems.length ? '已生成' : '待生成' }}</strong>
          </div>
          <div v-if="store.planItems.length" class="task-list">
            <label v-for="task in store.planItems.slice(0, 4)" :key="`${task.day}-${task.task}`">
              <input type="checkbox" />
              <span>第 {{ task.day }} 天：{{ task.task }}</span>
              <small>待完成</small>
            </label>
          </div>
          <p v-else class="muted-copy">还没有学习计划。请到“学习规划”页填写目标，或上传资料生成计划。</p>
          <div class="soft-progress"><i :style="{ width: store.planItems.length ? '8%' : '0%' }" /></div>
          <button class="soft-button" type="button" @click="activePage = 'planning'">去设置学习计划</button>
        </article>

        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">互动</span>
              <h2>学习探索舱</h2>
            </div>
            <span class="pulse-chip">{{ store.currentActivity ? '已准备' : '待生成' }}</span>
          </div>
          <p class="muted-copy">
            把计划变成知识地图、今日闯关或陪练流程，让 StudyPet 不只聊天，也陪你动手探索。
          </p>
          <button class="primary-button" type="button" @click="activePage = 'explore'">进入探索舱</button>
        </article>

        <article class="premium-card glass-card">
          <div class="card-title-row">
            <div>
              <span class="eyebrow">记录</span>
              <h2>学习热力</h2>
            </div>
            <strong>{{ store.checkins.length ? `${store.streakDays} 天连续` : '暂无' }}</strong>
          </div>
          <div class="heatmap" aria-label="学习热力图">
            <span v-for="(cell, index) in heatmapCells" :key="index" :data-level="cell" />
          </div>
          <p class="muted-copy">打卡后会逐步点亮你的学习热力图。</p>
        </article>
      </section>
    </section>

    <section v-else-if="activePage === 'planning'" class="page planning-page">
      <aside class="side-rail glass-card">
        <span class="eyebrow">目标</span>
        <h2>你的学习路线</h2>
        <p>这里不会预设任何学习内容。输入目标或上传资料后，AI 会生成属于你的计划。</p>
        <div class="rail-stat"><span>当前目标</span><strong>{{ store.examType || '待设置' }}</strong></div>
        <div class="rail-stat"><span>计划状态</span><strong>{{ store.planItems.length ? '已生成' : '待生成' }}</strong></div>
      </aside>

      <section class="roadmap glass-card">
        <div class="section-heading">
          <span class="eyebrow">学习路线</span>
          <h1>{{ store.weeklyPlanItems.length ? '阶段计划' : '暂无学习路线' }}</h1>
        </div>
        <div v-if="store.weeklyPlanItems.length" class="timeline-board">
          <article v-for="week in store.weeklyPlanItems" :key="week.week" class="day-column">
            <h3>第 {{ week.week }} 周</h3>
            <div class="roadmap-task" draggable="true">
              <strong>{{ week.goal }}</strong>
              <span>可根据实际进度调整</span>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">
          <strong>等待生成计划</strong>
          <span>填写右侧信息，或上传学习资料后生成。</span>
        </div>
      </section>

      <aside class="planner-assistant glass-card">
        <span class="eyebrow">AI 规划</span>
        <h2>生成你的学习计划</h2>
        <label><span>考试/学习目标</span><input v-model="store.examType" placeholder="例如：考研数学、英语四级、教师资格证" /></label>
        <label><span>目标分数</span><input v-model.number="store.targetScore" type="number" placeholder="例如：120" /></label>
        <label><span>剩余天数</span><input v-model.number="store.daysLeft" type="number" min="1" placeholder="例如：60" /></label>
        <label><span>当前水平</span><input v-model="store.currentLevel" placeholder="例如：基础薄弱 / 中等 / 较好" /></label>
        <label><span>补充目标</span><input v-model="store.goal" placeholder="例如：每天学习 2 小时，优先补函数" /></label>
        <button class="primary-button" type="button" @click="store.runPlan" :disabled="store.loading || !store.examType">生成学习计划</button>
        <label class="file-action">
          <span>上传学习资料生成计划</span>
          <input type="file" accept=".txt,.md,.docx,.pdf" @change="handleDocumentImport" />
        </label>
        <p v-if="store.documentSummary" class="muted-copy">{{ store.documentSummary }}</p>
        <p v-if="store.documentError" class="error-copy">{{ store.documentError }}</p>
      </aside>
    </section>

    <section v-else-if="activePage === 'explore'" class="page explore-page">
      <aside class="explore-menu glass-card">
        <span class="eyebrow">深度互动</span>
        <h2>学习探索舱</h2>
        <p>借鉴 OpenMAIC 的互动模式，但用 StudyPet 的方式呈现：结构化、可追踪、由桌宠陪你完成。</p>
        <div class="explore-type-list">
          <button
            v-for="type in interactiveTypes"
            :key="type.id"
            type="button"
            :class="{ active: store.interactiveType === type.id }"
            @click="store.interactiveType = type.id"
          >
            <strong>{{ type.title }}</strong>
            <span>{{ type.desc }}</span>
          </button>
        </div>
      </aside>

      <section class="explore-stage glass-card">
        <div class="section-heading">
          <span class="eyebrow">当前探索</span>
          <h1>{{ store.currentActivity?.title || '等待生成互动活动' }}</h1>
          <p>{{ store.currentActivity?.objective || '选择左侧模式，输入主题，生成一个可执行的小型互动学习活动。' }}</p>
        </div>

        <div v-if="store.currentActivity" class="activity-board">
          <div v-if="store.currentActivity.type === 'mindmap'" class="mindmap-board">
            <article
              v-for="node in store.currentActivity.nodes"
              :key="node.id"
              :class="['mindmap-node', { root: node.level === 0 }]"
            >
              <strong>{{ node.label }}</strong>
              <span>{{ node.status }}</span>
            </article>
          </div>

          <div class="activity-steps">
            <label v-for="step in store.currentActivity.steps" :key="step.id" class="activity-step">
              <input
                type="checkbox"
                :checked="store.completedInteractiveSteps.includes(step.id)"
                @change="store.toggleInteractiveStep(step.id)"
              />
              <span>
                <strong>{{ step.title }}</strong>
                <small>{{ step.description }}</small>
              </span>
            </label>
          </div>

          <div v-if="store.currentActivity.widgets.length" class="simulation-widgets">
            <label v-for="widget in store.currentActivity.widgets" :key="widget.id">
              <span>{{ widget.label }}</span>
              <input type="range" :min="widget.min" :max="widget.max" :value="widget.value" />
            </label>
          </div>

          <div class="explore-progress">
            <span>完成进度</span>
            <strong>{{ store.interactiveProgress }}%</strong>
            <div class="soft-progress"><i :style="{ width: `${store.interactiveProgress}%` }" /></div>
          </div>

          <div class="checkpoint-row">
            <span v-for="checkpoint in store.currentActivity.checkpoints" :key="checkpoint">{{ checkpoint }}</span>
          </div>

          <p class="muted-copy">完成规则：{{ store.currentActivity.completion_rule }}</p>
          <button class="primary-button" type="button" @click="store.completeInteractiveActivity" :disabled="store.loading">
            记录这次探索
          </button>
          <p v-if="store.interactiveResult" class="success-copy">
            {{ store.interactiveResult.message }} +{{ store.interactiveResult.exp }} EXP
          </p>
        </div>

        <div v-else class="empty-state">
          <strong>暂无互动内容</strong>
          <span>生成后会在这里显示知识地图、闯关步骤或互动小实验。</span>
        </div>
      </section>

      <aside class="explore-builder glass-card">
        <span class="eyebrow">生成器</span>
        <h2>创建探索活动</h2>
        <label><span>探索主题</span><input v-model="store.interactiveTopic" :placeholder="store.examType || '例如：导数基础、英语阅读、计算机网络'" /></label>
        <label>
          <span>补充材料</span>
          <textarea v-model="store.interactiveSourceText" placeholder="可粘贴一小段资料、薄弱点或今天想练的内容。" />
        </label>
        <button class="primary-button" type="button" @click="store.generateInteractiveActivity()" :disabled="store.loading">
          生成互动活动
        </button>
        <button class="soft-button" type="button" @click="store.generateInteractiveActivity('challenge')" :disabled="store.loading">
          直接生成今日闯关
        </button>
        <div class="pet-mini-card">
          <StudyPetAvatar @chat="activePage = 'home'" />
          <p>{{ store.companionMessage }}</p>
        </div>
      </aside>
    </section>

    <section v-else-if="activePage === 'checkin'" class="page checkin-page">
      <section class="streak-hero glass-card">
        <span class="eyebrow">连续打卡</span>
        <h1>{{ store.streakDays }} 天</h1>
        <p>{{ store.streakDays ? '继续保持你的节奏。' : '还没有打卡记录，先完成第一次学习记录吧。' }}</p>
      </section>

      <section class="checkin-center">
        <StudyPetAvatar @chat="activePage = 'growth'" />
        <div class="checkin-form glass-card">
          <label><span>学习科目</span><input v-model="store.checkinSubject" placeholder="例如：数学" /></label>
          <label><span>学习时长（分钟）</span><input v-model.number="store.checkinMinutes" type="number" min="1" placeholder="例如：45" /></label>
        </div>
        <button class="checkin-button" type="button" @click="completeCheckin">
          <span>完成今日打卡</span>
        </button>
        <div v-if="showCelebration" class="celebration-layer">
          <span>+1 记录</span>
          <span>继续积累</span>
          <span>StudyPet 已同步</span>
        </div>
      </section>

      <aside class="checkin-calendar glass-card">
        <span class="eyebrow">学习日历</span>
        <h2>{{ store.checkins.length ? '已开始记录' : '暂无学习记录' }}</h2>
        <div class="heatmap large">
          <span v-for="(cell, index) in heatmapCells" :key="`large-${index}`" :data-level="cell" />
        </div>
      </aside>

      <section class="stats-strip">
        <article class="glass-card"><span>总学习时长</span><strong>{{ store.todayStudyMinutes }} 分钟</strong></article>
        <article class="glass-card"><span>打卡记录</span><strong>{{ store.checkins.length }}</strong></article>
        <article class="glass-card"><span>今日科目</span><strong>{{ store.todaySubjects.length || '暂无' }}</strong></article>
        <article class="glass-card"><span>计划任务</span><strong>{{ store.planItems.length || '待生成' }}</strong></article>
      </section>
    </section>

    <section v-else class="page growth-page">
      <aside class="achievement-panel glass-card">
        <span class="eyebrow">成就</span>
        <h2>成长记录</h2>
        <div class="achievement-item">
          <span>{{ store.streakDays }}</span>
          <div><strong>连续打卡</strong><small>{{ store.streakDays ? '已经开始积累' : '暂无记录' }}</small></div>
        </div>
        <div class="achievement-item">
          <span>{{ store.planItems.length }}</span>
          <div><strong>计划任务</strong><small>{{ store.planItems.length ? '已生成计划' : '待生成' }}</small></div>
        </div>
        <div class="achievement-item">
          <span>{{ store.interactiveHistory.length }}</span>
          <div><strong>探索活动</strong><small>{{ store.interactiveHistory.length ? '已有互动活动' : '等待第一次探索' }}</small></div>
        </div>
      </aside>

      <section class="growth-center glass-card">
        <span class="eyebrow">我的学习旅程</span>
        <h1>{{ store.checkins.length || store.planItems.length ? 'StudyPet 正在和你一起成长' : '等待你的第一次行动' }}</h1>
        <StudyPetAvatar @chat="activePage = 'home'" />
        <div class="evolution-card">
          <span>当前阶段</span>
          <strong>{{ store.checkins.length ? '已开始学习记录' : '待创建学习目标' }}</strong>
          <div class="soft-progress"><i :style="{ width: store.checkins.length ? '12%' : '0%' }" /></div>
        </div>
        <div class="media-tools">
          <button class="soft-button" type="button" @click="store.generatePetConcept">生成桌宠概念图</button>
          <button class="soft-button" type="button" @click="store.speakCompanionMessage">朗读当前回复</button>
          <button class="soft-button" type="button" @click="store.loadEvents">查看保存记录</button>
        </div>
        <img v-if="store.generatedImageUrl" class="generated-preview" :src="store.generatedImageUrl" alt="生成的 StudyPet 概念图" />
        <audio v-if="store.ttsAudioUrl" controls :src="store.ttsAudioUrl" />
        <p v-if="store.generatedImageError" class="error-copy">{{ store.generatedImageError }}</p>
        <p v-if="store.ttsError" class="error-copy">{{ store.ttsError }}</p>
      </section>

      <aside class="abilities-panel glass-card">
        <span class="eyebrow">能力</span>
        <h2>已接入能力</h2>
        <div class="ability-item"><strong>AI 计划生成</strong><span>{{ store.planItems.length ? '已可使用' : '等待目标输入' }}</span></div>
        <div class="ability-item"><strong>流式陪伴聊天</strong><span>{{ store.chatHistory.length ? '已有对话' : '可随时开始' }}</span></div>
        <div class="ability-item"><strong>学习探索舱</strong><span>{{ store.currentActivity ? '已生成活动' : '可创建互动练习' }}</span></div>
        <div class="ability-item"><strong>学习打卡</strong><span>{{ store.checkins.length ? '已有记录' : '等待第一次打卡' }}</span></div>
      </aside>

      <section class="growth-timeline glass-card">
        <span class="eyebrow">最近记录</span>
        <div v-if="store.events.length" class="event-list">
          <article v-for="event in store.events" :key="event.id">
            <strong>{{ event.event_type }}</strong>
            <span>{{ new Date(event.created_at).toLocaleString() }}</span>
          </article>
        </div>
        <div v-else class="empty-state">
          <strong>暂无保存记录</strong>
          <span>点击“查看保存记录”后会显示数据库中的最近事件。</span>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import StudyPetAvatar from './components/StudyPetAvatar.vue'
import { useStudyStore } from './stores/useStudyStore'

type PageId = 'home' | 'planning' | 'explore' | 'checkin' | 'growth'
type InteractiveType = 'mindmap' | 'challenge' | 'simulation' | 'coach_practice'

const store = useStudyStore()
const activePage = ref<PageId>('home')
const showCelebration = ref(false)

const navItems: Array<{ id: PageId; label: string }> = [
  { id: 'home', label: '今日' },
  { id: 'planning', label: '学习规划' },
  { id: 'explore', label: '学习探索舱' },
  { id: 'checkin', label: '学习打卡' },
  { id: 'growth', label: '成长中心' },
]

const interactiveTypes: Array<{ id: InteractiveType; title: string; desc: string }> = [
  { id: 'mindmap', title: '知识地图', desc: '把目标拆成可点击的结构' },
  { id: 'challenge', title: '今日闯关', desc: '把任务变成 3 个轻量关卡' },
  { id: 'simulation', title: '互动小实验', desc: '用参数和观察建立直觉' },
  { id: 'coach_practice', title: 'AI 陪练室', desc: 'StudyPet 陪你完成短练习' },
]

const heatmapCells = computed(() =>
  Array.from({ length: 35 }, (_, index) => (index < store.checkins.length ? Math.min(4, store.checkins[index]?.minutes ? 2 : 1) : 0)),
)

function completeCheckin() {
  store.addCheckin()
  showCelebration.value = true
  window.setTimeout(() => {
    showCelebration.value = false
  }, 1800)
}

function handleDocumentImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  store.runPlanFromDocument(file)
  input.value = ''
}
</script>
