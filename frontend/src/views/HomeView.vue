<template>
  <div>
    <section class="hero">
      <div class="container hero__content">
        <div>
          <h1>Top Scoot</h1>
          <p>Главный рейтинг райдеров самокатной сцены России. Только официальные результаты, прозрачные правила и честная конкуренция.</p>
          <div class="hero__actions">
            <RouterLink to="/rating" class="cta">Смотреть рейтинг</RouterLink>
            <RouterLink to="/contact" class="cta secondary">Предложить турнир</RouterLink>
          </div>
        </div>
        <div class="hero__meta">
          <div class="meta-card">
            <span class="meta-card__label">Обновление</span>
            <span class="meta-card__value">каждый месяц</span>
          </div>
          <div class="meta-card">
            <span class="meta-card__label">Сезон</span>
            <span class="meta-card__value">скользящие 90 дней</span>
          </div>
          <div class="meta-card">
            <span class="meta-card__label">Очки</span>
            <span class="meta-card__value">по уровню турнира</span>
          </div>
        </div>
      </div>
    </section>

    <section class="top-section">
      <div class="container top-section__inner">
        <div class="top-section__header">
          <h2>Топ-10 сезона</h2>
          <RouterLink to="/rating" class="link">Весь рейтинг →</RouterLink>
        </div>
        <ElTable :data="topRiders" v-loading="loading" class="top-table" size="large">
          <ElTableColumn type="index" label="Место" width="90" />
          <ElTableColumn prop="nickname" label="Ник" min-width="160">
            <template #default="scope">
              <RouterLink :to="`/r/${scope.row.id}`" class="table-link">{{ scope.row.nickname }}</RouterLink>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="city" label="Город" width="180" />
          <ElTableColumn prop="level" label="Уровень" width="140">
            <template #default="scope">
              <span class="badge" :class="`badge--${scope.row.level}`">{{ levelLabel(scope.row.level) }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="style" label="Стиль" width="140">
            <template #default="scope">
              <span class="tag">{{ styleLabel(scope.row.style) }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="seasonPoints" label="Очки" width="120" align="right" />
        </ElTable>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElTable, ElTableColumn } from 'element-plus'
import api from '../api'

const topRiders = ref([])
const loading = ref(false)

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

async function fetchTop() {
  loading.value = true
  try {
    const response = await api.get('/api/rating', { params: { limit: 10, page: 1 } })
    topRiders.value = response.data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchTop)
</script>

<style scoped>
.hero {
  padding: 80px 0 60px;
  background: linear-gradient(135deg, #000 0%, #E53935 100%);
  color: #fff;
}

.hero__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

h1 {
  font-size: 50px;
  margin-bottom: 16px;
}

.hero p {
  font-size: 18px;
  line-height: 1.6;
  max-width: 520px;
}

.hero__actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.cta {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  text-decoration: none;
  background: #fff;
  color: #000;
}

.cta.secondary {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.hero__meta {
  display: grid;
  gap: 12px;
}

.meta-card {
  padding: 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
}

.meta-card__label {
  font-size: 12px;
  text-transform: uppercase;
  opacity: 0.8;
}

.meta-card__value {
  display: block;
  font-size: 16px;
  font-weight: 600;
}

.top-section {
  padding: 60px 0;
  background: #fff;
}

.top-section__inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.top-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h2 {
  font-size: 32px;
  margin: 0;
}

.link {
  color: #E53935;
  text-decoration: none;
  font-weight: 600;
}

.top-table {
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

.badge--novice {
  background: #9e9e9e;
}

.badge--amateur {
  background: #1e88e5;
}

.badge--pro {
  background: #E53935;
}

.tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f1f1f1;
  font-size: 12px;
}

@media (max-width: 900px) {
  .hero__content {
    flex-direction: column;
    align-items: flex-start;
  }
  .hero p {
    max-width: none;
  }
  .hero__meta {
    width: 100%;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
}

@media (max-width: 600px) {
  h1 {
    font-size: 36px;
  }
  .hero__actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
