<template>
  <div>
    <div class="toolbar">
      <ElInput
        v-model="filters.search"
        placeholder="Поиск по названию"
        clearable
        class="toolbar__input"
        @keyup.enter="refresh"
        @clear="refresh"
      >
        <template #prefix>
          <ElIcon><Search /></ElIcon>
        </template>
      </ElInput>
      <ElInput
        v-model="filters.city"
        placeholder="Город"
        clearable
        class="toolbar__input toolbar__input--small"
        @keyup.enter="refresh"
        @clear="refresh"
      />
      <ElSelect v-model="filters.level" placeholder="Уровень" clearable class="toolbar__select" @change="refresh">
        <ElOption label="Local" value="local" />
        <ElOption label="Regional" value="regional" />
        <ElOption label="National" value="national" />
        <ElOption label="International" value="international" />
      </ElSelect>
      <ElSelect v-model="filters.status" placeholder="Статус" clearable class="toolbar__select" @change="refresh">
        <ElOption label="Черновик" value="draft" />
        <ElOption label="Опубликован" value="published" />
      </ElSelect>
      <ElDatePicker
        v-model="filters.dateRange"
        type="daterange"
        start-placeholder="Дата от"
        end-placeholder="Дата до"
        value-format="YYYY-MM-DD"
        unlink-panels
        @change="refresh"
      />
      <ElButton type="primary" :icon="Plus" @click="openCreate">Добавить</ElButton>
    </div>

    <ElTable :data="items" v-loading="loading" height="520" stripe>
      <ElTableColumn prop="name" label="Название" min-width="200" />
      <ElTableColumn prop="city" label="Город" width="150" />
      <ElTableColumn prop="level" label="Уровень" width="140" />
      <ElTableColumn prop="dateStart" label="Дата начала" width="140" />
      <ElTableColumn prop="dateEnd" label="Дата окончания" width="140" />
      <ElTableColumn prop="participantsCount" label="Участники" width="120" />
      <ElTableColumn prop="style" label="Стиль" width="120" />
      <ElTableColumn prop="status" label="Статус" width="140">
        <template #default="scope">
          <ElTag :type="scope.row.status === 'published' ? 'success' : 'info'">
            {{ scope.row.status === 'published' ? 'Опубликован' : 'Черновик' }}
          </ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn label="Действия" width="200" fixed="right">
        <template #default="scope">
          <ElButton size="small" :icon="Edit" @click="openEdit(scope.row)"></ElButton>
          <ElButton
            size="small"
            type="success"
            :disabled="scope.row.status === 'published'"
            :icon="Upload"
            @click="publish(scope.row)"
          ></ElButton>
        </template>
      </ElTableColumn>
    </ElTable>

    <div class="table-footer">
      <ElPagination
        layout="prev, pager, next, jumper"
        :current-page="pagination.page"
        :page-size="pagination.limit"
        :total="pagination.total"
        @current-change="handlePageChange"
      />
    </div>

    <ElDialog v-model="dialog.visible" :title="dialog.title" width="640px">
      <ElForm :model="form" label-position="top" :disabled="dialog.saving">
        <ElFormItem label="Название" required>
          <ElInput v-model="form.name" />
        </ElFormItem>
        <ElFormItem label="Город" required>
          <ElInput v-model="form.city" />
        </ElFormItem>
        <ElFormItem label="Даты" required>
          <ElDatePicker
            v-model="form.dates"
            type="daterange"
            start-placeholder="Дата начала"
            end-placeholder="Дата окончания"
            value-format="YYYY-MM-DD"
            unlink-panels
            :default-time="['09:00:00', '18:00:00']"
          />
        </ElFormItem>
        <ElFormItem label="Уровень" required>
          <ElSelect v-model="form.level">
            <ElOption label="Local" value="local" />
            <ElOption label="Regional" value="regional" />
            <ElOption label="National" value="national" />
            <ElOption label="International" value="international" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Количество участников">
          <ElInputNumber v-model="form.participantsCount" :min="0" :max="500" controls-position="right" />
        </ElFormItem>
        <ElFormItem label="Стиль">
          <ElSelect v-model="form.style" clearable placeholder="Не указан">
            <ElOption label="Street" value="street" />
            <ElOption label="Park" value="park" />
            <ElOption label="Universal" value="universal" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Есть best trick?">
          <ElSwitch v-model="form.hasBestTrick" />
        </ElFormItem>
        <ElFormItem label="Статус">
          <ElSelect v-model="form.status">
            <ElOption label="Черновик" value="draft" />
            <ElOption label="Опубликован" value="published" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Ссылка на источник">
          <ElInput v-model="form.sourceUrl" />
        </ElFormItem>
        <ElFormItem label="Контакты организатора">
          <ElInput v-model="form.organizerContact" type="textarea" rows="2" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <div class="dialog-footer">
          <ElButton @click="dialog.visible = false">Отмена</ElButton>
          <ElButton type="primary" :loading="dialog.saving" @click="saveEvent">Сохранить</ElButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { Search, Plus, Edit, Upload } from '@element-plus/icons-vue'
import { ElNotification, ElMessageBox } from 'element-plus'
import api from '../api'

const items = ref([])
const loading = ref(false)
const filters = reactive({
  search: '',
  city: '',
  level: '',
  status: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const dialog = reactive({
  visible: false,
  title: '',
  saving: false
})

const form = reactive({
  id: null,
  name: '',
  city: '',
  dates: [],
  level: 'local',
  participantsCount: null,
  style: '',
  hasBestTrick: false,
  status: 'draft',
  sourceUrl: '',
  organizerContact: ''
})

async function fetchEvents() {
  loading.value = true
  try {
    const params = {
      search: filters.search,
      city: filters.city,
      level: filters.level,
      status: filters.status,
      page: pagination.page,
      limit: pagination.limit
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.date_from = filters.dateRange[0]
      params.date_to = filters.dateRange[1]
    }
    const response = await api.get('/api/admin/events', { params })
    items.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElNotification.error({ title: 'Ошибка', message: 'Не удалось загрузить турниры' })
  } finally {
    loading.value = false
  }
}

function refresh() {
  pagination.page = 1
  fetchEvents()
}

function handlePageChange(page) {
  pagination.page = page
  fetchEvents()
}

function resetForm() {
  form.id = null
  form.name = ''
  form.city = ''
  form.dates = []
  form.level = 'local'
  form.participantsCount = null
  form.style = ''
  form.hasBestTrick = false
  form.status = 'draft'
  form.sourceUrl = ''
  form.organizerContact = ''
}

function openCreate() {
  resetForm()
  dialog.title = 'Новый турнир'
  dialog.visible = true
}

function openEdit(row) {
  resetForm()
  form.id = row.id
  form.name = row.name
  form.city = row.city
  form.dates = [row.dateStart, row.dateEnd || row.dateStart]
  form.level = row.level
  form.participantsCount = row.participantsCount
  form.style = row.style || ''
  form.hasBestTrick = !!row.hasBestTrick
  form.status = row.status
  form.sourceUrl = row.sourceUrl || ''
  form.organizerContact = row.organizerContact || ''
  dialog.title = 'Редактировать турнир'
  dialog.visible = true
}

async function saveEvent() {
  dialog.saving = true
  try {
    if (!form.dates || form.dates.length === 0) {
      throw new Error('Нужно выбрать даты')
    }
    const payload = {
      name: form.name,
      city: form.city,
      date_start: form.dates[0],
      date_end: form.dates[1] || form.dates[0],
      level: form.level,
      participants_count: form.participantsCount,
      style: form.style || null,
      has_best_trick: form.hasBestTrick,
      status: form.status,
      source_url: form.sourceUrl,
      organizer_contact: form.organizerContact
    }
    if (form.id) {
      await api.put(`/api/admin/events/${form.id}`, payload)
      ElNotification.success({ title: 'Сохранено', message: 'Турнир обновлён' })
    } else {
      await api.post('/api/admin/events', payload)
      ElNotification.success({ title: 'Создано', message: 'Турнир добавлен' })
    }
    dialog.visible = false
    fetchEvents()
  } catch (error) {
    const message = error?.message || error?.response?.data?.errors?.join(', ') || 'Не удалось сохранить турнир'
    ElNotification.error({ title: 'Ошибка', message })
  } finally {
    dialog.saving = false
  }
}

async function publish(row) {
  try {
    await ElMessageBox.confirm(
      `Опубликовать турнир «${row.name}»?`,
      'Подтверждение',
      {
        type: 'warning',
        confirmButtonText: 'Опубликовать',
        cancelButtonText: 'Отмена'
      }
    )
    await api.post(`/api/admin/events/${row.id}/publish`)
    ElNotification.success({ title: 'Опубликовано', message: 'Турнир опубликован' })
    fetchEvents()
  } catch (error) {
    if (error !== 'cancel') {
      const message = error?.response?.data?.error || 'Не удалось опубликовать турнир'
      ElNotification.error({ title: 'Ошибка', message })
    }
  }
}

onMounted(() => {
  fetchEvents()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar__input {
  flex: 1 1 220px;
}

.toolbar__input--small {
  max-width: 220px;
}

.toolbar__select {
  width: 200px;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
