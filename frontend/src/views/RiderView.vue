<template>
  <div class="section">
    <div class="container" v-if="loading">
      <ElSkeleton animated :rows="6" />
    </div>

    <div class="container" v-else-if="rider">
      <RouterLink to="/rating" class="back">← К рейтингу</RouterLink>
      <div class="profile">
        <div>
          <h1>{{ rider.nickname }}</h1>
          <p v-if="rider.fullname" class="fullname">{{ rider.fullname }}</p>
          <div class="meta">
            <span>{{ rider.city }}</span>
            <span v-if="rider.age">{{ rider.age }} лет</span>
            <span class="badge" :class="`badge--${rider.level}`">{{ levelLabel(rider.level) }}</span>
            <span class="tag">{{ styleLabel(rider.style) }}</span>
          </div>
        </div>
        <div class="points">
          <div class="points__value">{{ rider.seasonPoints }}</div>
          <div class="points__label">Очков за текущий сезон</div>
        </div>
      </div>

      <section class="results">
        <div class="results__header">
          <h2>Результаты сезона</h2>
          <p>Отображаются турниры текущего 90-дневного периода.</p>
        </div>
        <ElTable :data="seasonResults" stripe>
          <ElTableColumn prop="eventDate" label="Дата" width="140" />
          <ElTableColumn prop="eventName" label="Турнир" min-width="200">
            <template #default="scope">
              <RouterLink :to="`/e/${scope.row.eventId}`" class="table-link">{{ scope.row.eventName }}</RouterLink>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="eventCity" label="Город" width="160" />
          <ElTableColumn prop="eventLevel" label="Уровень" width="140">
            <template #default="scope">
              <span class="badge" :class="`badge--${scope.row.eventLevel}`">{{ levelLabel(scope.row.eventLevel) }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="place" label="Место" width="120" />
          <ElTableColumn prop="points" label="Очки" width="120" align="right" />
          <ElTableColumn prop="isFinalist" label="Статус" width="140">
            <template #default="scope">
              <span v-if="scope.row.isFinalist" class="tag">Финалист</span>
              <span v-else-if="scope.row.isParticipant" class="tag">Участник</span>
            </template>
          </ElTableColumn>
        </ElTable>
      </section>
    </div>

    <div v-else class="container empty">
      <ElEmpty description="Райдер не найден" />
      <RouterLink to="/rating" class="back">Вернуться к рейтингу</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const route = useRoute()
const rider = ref(null)
const seasonResults = ref([])
const loading = ref(false)

function levelLabel(level) {
  const map = {
    novice: 'Новичок',
    amateur: 'Любитель',
    pro: 'Про',
    local: 'Локальный',
    regional: 'Региональный',
    national: 'Нац',
    international: 'Междунар'
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

async function fetchRider() {
  loading.value = true
  rider.value = null
  seasonResults.value = []
  try {
    const response = await api.get(`/api/riders/${props.id}`)
    rider.value = response.data.rider
    seasonResults.value = response.data.seasonResults
  } catch (error) {
    rider.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchRider)

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId !== oldId) {
      fetchRider()
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

.profile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.fullname {
  margin-top: -8px;
  color: #555;
}

.meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 12px;
  font-size: 14px;
}

.badge {
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  text-transform: uppercase;
}

.badge--novice { background: #9e9e9e; }
.badge--amateur { background: #1e88e5; }
.badge--pro { background: #E53935; }
.badge--local { background: #9e9e9e; }
.badge--regional { background: #42a5f5; }
.badge--national { background: #fb8c00; }
.badge--international { background: #8e24aa; }

.tag {
  background: #f1f1f1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.points {
  text-align: right;
}

.points__value {
  font-size: 42px;
  font-weight: 700;
  color: #E53935;
}

.points__label {
  font-size: 14px;
  color: #666;
}

.results__header {
  margin-bottom: 16px;
}

.results__header h2 {
  margin-bottom: 4px;
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
  .profile {
    flex-direction: column;
    align-items: flex-start;
  }
  .points {
    text-align: left;
  }
}
</style>
