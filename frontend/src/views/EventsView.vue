<template>
  <div class="section">
    <div class="container">
      <div class="section__header">
        <div>
          <h1>Турниры</h1>
          <p>Публикуем итоговые протоколы последних соревнований. Можно фильтровать по уровню и городу.</p>
        </div>
        <RouterLink to="/contact" class="cta">Предложить турнир</RouterLink>
      </div>

      <div class="filters">
        <ElSelect v-model="filters.level" placeholder="Уровень" clearable @change="fetchEvents">
          <ElOption label="Local" value="local" />
          <ElOption label="Regional" value="regional" />
          <ElOption label="National" value="national" />
          <ElOption label="International" value="international" />
        </ElSelect>
        <ElInput
          v-model="filters.city"
          placeholder="Город"
          clearable
          @clear="fetchEvents"
          @keyup.enter="fetchEvents"
        />
      </div>

      <ElTable :data="events" v-loading="loading" stripe class="events-table">
        <ElTableColumn prop="dateStart" label="Дата" width="140" />
        <ElTableColumn prop="name" label="Название" min-width="220">
          <template #default="scope">
            <RouterLink :to="`/e/${scope.row.id}`" class="table-link">{{ scope.row.name }}</RouterLink>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="city" label="Город" width="160" />
        <ElTableColumn prop="level" label="Уровень" width="140">
          <template #default="scope">
            <span class="badge" :class="`badge--${scope.row.level}`">{{ levelLabel(scope.row.level) }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="participants" label="Участники" width="140" align="right" />
        <ElTableColumn prop="style" label="Стиль" width="140">
          <template #default="scope">
            <span v-if="scope.row.style" class="tag">{{ styleLabel(scope.row.style) }}</span>
            <span v-else class="muted">—</span>
          </template>
        </ElTableColumn>
      </ElTable>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import api from '../api'

const events = ref([])
const loading = ref(false)
const filters = reactive({ level: '', city: '' })

function levelLabel(level) {
  const map = {
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

async function fetchEvents() {
  loading.value = true
  try {
    const params = {
      level: filters.level || undefined,
      city: filters.city || undefined
    }
    const response = await api.get('/api/events', { params })
    events.value = response.data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchEvents)
</script>

<style scoped>
.section {
  padding: 50px 0 80px;
  background: #fff;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.cta {
  color: #E53935;
  text-decoration: none;
  font-weight: 600;
}

.events-table {
  --el-table-header-bg-color: #fafafa;
}

.table-link {
  color: #000;
  text-decoration: none;
  font-weight: 600;
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

.tag {
  background: #f1f1f1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.muted {
  color: #999;
}

@media (max-width: 768px) {
  .section__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
