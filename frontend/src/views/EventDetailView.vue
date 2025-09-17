<template>
  <div class="section">
    <div class="container" v-if="loading">
      <ElSkeleton animated :rows="6" />
    </div>

    <div class="container" v-else-if="event">
      <RouterLink to="/events" class="back">← К списку турниров</RouterLink>

      <header class="header">
        <div>
          <h1>{{ event.name }}</h1>
          <p class="meta">
            <span>{{ event.city }}</span>
            <span>{{ formatDates(event.dateStart, event.dateEnd) }}</span>
            <span class="badge" :class="`badge--${event.level}`">{{ levelLabel(event.level) }}</span>
            <span v-if="event.style" class="tag">{{ styleLabel(event.style) }}</span>
          </p>
        </div>
        <ElButton type="primary" plain disabled>Скачать CSV (скоро)</ElButton>
      </header>

      <div class="details">
        <div class="details__item">
          <span class="label">Участников</span>
          <span class="value">{{ event.participants || '—' }}</span>
        </div>
        <div class="details__item">
          <span class="label">Best Trick</span>
          <span class="value">{{ event.hasBestTrick ? 'Есть' : 'Нет' }}</span>
        </div>
        <div class="details__item" v-if="event.sourceUrl">
          <span class="label">Источник</span>
          <a :href="event.sourceUrl" target="_blank" rel="noopener" class="value">Перейти</a>
        </div>
        <div class="details__item" v-if="event.organizerContact">
          <span class="label">Контакты</span>
          <span class="value">{{ event.organizerContact }}</span>
        </div>
      </div>

      <section class="results">
        <h2>Итоги</h2>
        <ElTable :data="results" stripe>
          <ElTableColumn prop="place" label="Место" width="100" />
          <ElTableColumn prop="nickname" label="Ник / Имя" min-width="200">
            <template #default="scope">
              <RouterLink :to="`/r/${scope.row.riderId}`" class="table-link">{{ scope.row.nickname }}</RouterLink>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="city" label="Город" width="160" />
          <ElTableColumn prop="riderLevel" label="Уровень" width="140">
            <template #default="scope">
              <span class="badge" :class="`badge--${scope.row.riderLevel}`">{{ levelLabel(scope.row.riderLevel) }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="points" label="Очки" width="120" align="right" />
          <ElTableColumn label="Статус" width="140">
            <template #default="scope">
              <span v-if="scope.row.isFinalist" class="tag">Финалист</span>
              <span v-else-if="scope.row.isParticipant" class="tag">Участник</span>
            </template>
          </ElTableColumn>
        </ElTable>
      </section>
    </div>

    <div v-else class="container empty">
      <ElEmpty description="Турнир не найден" />
      <RouterLink to="/events" class="back">Вернуться к списку</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const route = useRoute()
const event = ref(null)
const results = ref([])
const loading = ref(false)

function levelLabel(level) {
  const map = {
    local: 'Локальный',
    regional: 'Региональный',
    national: 'Нац',
    international: 'Междунар',
    novice: 'Новичок',
    amateur: 'Любитель',
    pro: 'Про'
  }
  return map[level] || level
}

function styleLabel(style) {
  const map = {
    street: 'Street',
    park: 'Park',
    universal: 'Uni'
  }
  return map[style] || style
}

function formatDates(start, end) {
  if (!end || end === start) return start
  return `${start} — ${end}`
}

async function fetchEvent() {
  loading.value = true
  event.value = null
  results.value = []
  try {
    const response = await api.get(`/api/events/${props.id}`)
    event.value = response.data.event
    results.value = response.data.results
  } catch (error) {
    event.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchEvent)

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId !== oldId) {
      fetchEvent()
    }
  }
)
</script>

<style scoped>
.section {
  padding: 40px 0 80px;
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 24px;
}

.back {
  display: inline-block;
  margin-bottom: 16px;
  color: #E53935;
  text-decoration: none;
  font-weight: 600;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 12px;
  color: #555;
}

.badge {
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  text-transform: uppercase;
}

.badge--local { background: #9e9e9e; }
.badge--regional { background: #42a5f5; }
.badge--national { background: #fb8c00; }
.badge--international { background: #8e24aa; }
.badge--novice { background: #9e9e9e; }
.badge--amateur { background: #1e88e5; }
.badge--pro { background: #E53935; }

.tag {
  background: #f1f1f1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
  background: #fafafa;
  padding: 20px;
  border-radius: 12px;
}

.details__item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  text-transform: uppercase;
  color: #777;
}

.value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.table-link {
  color: #000;
  text-decoration: none;
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: 80px 0;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
