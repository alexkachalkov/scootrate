<template>
  <div class="section">
    <div class="container">
      <div class="section__header">
        <div>
          <h1>Рейтинг райдеров</h1>
          <p>Фильтры помогают сузить выбор по городу, уровню, стилю и возрасту. Поиск работает по нику и ФИО.</p>
        </div>
        <ElButton type="primary" @click="resetFilters" plain>Сбросить фильтры</ElButton>
      </div>

      <div class="filters">
        <ElInput
          v-model="filters.search"
          placeholder="Поиск по нику или ФИО"
          clearable
          @clear="refresh"
          @keyup.enter="refresh"
        >
          <template #prefix>
            <ElIcon><Search /></ElIcon>
          </template>
        </ElInput>
        <ElInput
          v-model="filters.city"
          placeholder="Город"
          clearable
          @clear="refresh"
          @keyup.enter="refresh"
        />
        <ElSelect v-model="filters.level" placeholder="Уровень" clearable @change="refresh">
          <ElOption label="Новичок" value="novice" />
          <ElOption label="Любитель" value="amateur" />
          <ElOption label="Про" value="pro" />
        </ElSelect>
        <ElSelect v-model="filters.style" placeholder="Стиль" clearable @change="refresh">
          <ElOption label="Street" value="street" />
          <ElOption label="Park" value="park" />
          <ElOption label="Universal" value="universal" />
        </ElSelect>
      </div>

      <div class="age-filter">
        <div class="age-filter__label">Возрастной диапазон</div>
        <ElSlider
          v-model="filters.ageRange"
          range
          :min="7"
          :max="25"
          :step="1"
          :disabled="filters.allAges"
          @change="refresh"
        />
        <ElCheckbox v-model="filters.allAges" @change="refresh">Показывать всех</ElCheckbox>
      </div>

      <ElTable
        :data="items"
        v-loading="loading"
        height="620"
        stripe
        @row-click="goToRider"
        class="rating-table"
      >
        <ElTableColumn type="index" label="Место" width="90" />
        <ElTableColumn prop="nickname" label="Ник / Имя" min-width="220">
          <template #default="scope">
            <div class="name-cell">
              <span class="nickname">{{ scope.row.nickname }}</span>
              <span class="fullname" v-if="scope.row.fullname">{{ scope.row.fullname }}</span>
            </div>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="city" label="Город" width="160" />
        <ElTableColumn prop="age" label="Возраст" width="120" />
        <ElTableColumn prop="level" label="Уровень" width="130">
          <template #default="scope">
            <span class="badge" :class="`badge--${scope.row.level}`">{{ levelLabel(scope.row.level) }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="style" label="Стиль" width="120">
          <template #default="scope">
            <span class="tag">{{ styleLabel(scope.row.style) }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="seasonPoints" label="Очки сезона" width="150" align="right" />
      </ElTable>

      <div class="table-footer">
        <ElPagination
          layout="prev, pager, next, jumper"
          :page-size="pagination.limit"
          :current-page="pagination.page"
          :total="pagination.total"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const items = ref([])
const loading = ref(false)

const filters = reactive({
  search: '',
  city: '',
  level: '',
  style: '',
  ageRange: [7, 25],
  allAges: false
})

const pagination = reactive({
  page: 1,
  limit: 50,
  total: 0
})

function levelLabel(level) {
  const map = {
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

async function fetchRating() {
  loading.value = true
  try {
    const params = {
      search: filters.search || undefined,
      city: filters.city || undefined,
      level: filters.level || undefined,
      style: filters.style || undefined,
      page: pagination.page,
      limit: pagination.limit
    }
    if (!filters.allAges) {
      params.ageMin = filters.ageRange[0]
      params.ageMax = filters.ageRange[1]
    } else {
      params.allAges = 1
    }
    const response = await api.get('/api/rating', { params })
    items.value = response.data.items
    pagination.total = response.data.total
  } finally {
    loading.value = false
  }
}

function refresh() {
  pagination.page = 1
  fetchRating()
}

function resetFilters() {
  filters.search = ''
  filters.city = ''
  filters.level = ''
  filters.style = ''
  filters.ageRange = [7, 25]
  filters.allAges = false
  refresh()
}

function handlePageChange(page) {
  pagination.page = page
  fetchRating()
}

function goToRider(row) {
  router.push({ name: 'rider', params: { id: row.id } })
}

onMounted(fetchRating)
</script>

<style scoped>
.section {
  padding: 50px 0;
  background: #fafafa;
}

.container {
  max-width: 1150px;
  margin: 0 auto;
  padding: 0 24px;
}

.section__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.section__header h1 {
  margin-bottom: 8px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.age-filter {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.age-filter__label {
  font-weight: 600;
}

.rating-table {
  cursor: pointer;
}

.name-cell {
  display: flex;
  flex-direction: column;
}

.fullname {
  font-size: 13px;
  color: #606266;
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

.tag {
  background: #f1f1f1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0 0;
}

@media (max-width: 768px) {
  .section__header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
