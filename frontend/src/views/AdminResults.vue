<template>
  <div>
    <div class="toolbar">
      <ElSelect
        v-model="selectedEvent"
        placeholder="Выберите турнир"
        filterable
        class="toolbar__select"
        @change="fetchResults"
      >
        <ElOption
          v-for="event in events"
          :key="event.id"
          :label="`${event.name} (${event.dateStart})`"
          :value="event.id"
        />
      </ElSelect>
      <ElButton type="primary" @click="refresh" :disabled="!selectedEvent" :loading="loading">
        Обновить
      </ElButton>
    </div>

    <ElTable :data="results" v-loading="loading" height="520" stripe>
      <ElTableColumn prop="riderId" label="ID райдера" width="120" />
      <ElTableColumn prop="place" label="Место" width="100" />
      <ElTableColumn prop="points" label="Очки" width="120" />
      <ElTableColumn label="Финалист" width="120">
        <template #default="scope">
          <ElTag type="info" v-if="scope.row.isFinalist">Финалист</ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn label="Участник" width="120">
        <template #default="scope">
          <ElTag type="info" v-if="scope.row.isParticipant">Участник</ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="comment" label="Комментарий" min-width="200" />
      <ElTableColumn label="Действия" width="140" fixed="right">
        <template #default="scope">
          <ElButton size="small" :icon="Edit" @click="openEdit(scope.row)"></ElButton>
        </template>
      </ElTableColumn>
    </ElTable>

    <ElDialog v-model="dialog.visible" :title="dialog.title" width="480px">
      <ElForm :model="form" label-position="top" :disabled="dialog.saving">
        <ElFormItem label="Место">
          <ElInputNumber v-model="form.place" :min="1" :max="200" />
        </ElFormItem>
        <ElFormItem label="Финалист">
          <ElSwitch v-model="form.isFinalist" />
        </ElFormItem>
        <ElFormItem label="Участник">
          <ElSwitch v-model="form.isParticipant" />
        </ElFormItem>
        <ElFormItem label="Очки">
          <ElInputNumber v-model="form.points" :min="0" :max="2000" :disabled="!isAdmin" />
          <p v-if="!isAdmin" class="hint">Изменять очки может только администратор</p>
        </ElFormItem>
        <ElFormItem label="Комментарий">
          <ElInput v-model="form.comment" type="textarea" rows="3" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <div class="dialog-footer">
          <ElButton @click="dialog.visible = false">Отмена</ElButton>
          <ElButton type="primary" :loading="dialog.saving" @click="saveResult">Сохранить</ElButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'
import api from '../api'
import { useAuthState } from '../stores/auth'

const events = ref([])
const selectedEvent = ref(null)
const results = ref([])
const loading = ref(false)

const dialog = reactive({
  visible: false,
  title: '',
  saving: false
})

const form = reactive({
  id: null,
  place: null,
  isFinalist: false,
  isParticipant: true,
  points: 0,
  comment: ''
})

const auth = useAuthState()
const isAdmin = computed(() => auth.user?.role === 'admin')

async function fetchEvents() {
  try {
    const response = await api.get('/api/admin/events', { params: { status: 'published', limit: 200 } })
    events.value = response.data.items
    if (!selectedEvent.value && events.value.length > 0) {
      selectedEvent.value = events.value[0].id
      await fetchResults()
    }
  } catch (error) {
    ElNotification.error({ title: 'Ошибка', message: 'Не удалось загрузить турниры' })
  }
}

async function fetchResults() {
  if (!selectedEvent.value) return
  loading.value = true
  try {
    const response = await api.get('/api/admin/results', { params: { eventId: selectedEvent.value } })
    results.value = response.data.items
  } catch (error) {
    ElNotification.error({ title: 'Ошибка', message: 'Не удалось загрузить результаты' })
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchResults()
}

function openEdit(row) {
  form.id = row.id
  form.place = row.place
  form.isFinalist = row.isFinalist
  form.isParticipant = row.isParticipant
  form.points = row.points
  form.comment = row.comment || ''
  dialog.title = `Результат райдера #${row.riderId}`
  dialog.visible = true
}

async function saveResult() {
  if (!form.id) return
  dialog.saving = true
  try {
    const payload = {
      place: form.place,
      isFinalist: form.isFinalist,
      isParticipant: form.isParticipant,
      comment: form.comment
    }
    if (isAdmin.value) {
      payload.points = form.points
    }
    await api.put(`/api/admin/results/${form.id}`, payload)
    ElNotification.success({ title: 'Сохранено', message: 'Результат обновлён' })
    dialog.visible = false
    fetchResults()
  } catch (error) {
    const message = error?.response?.data?.error || 'Не удалось сохранить результат'
    ElNotification.error({ title: 'Ошибка', message })
  } finally {
    dialog.saving = false
  }
}

onMounted(async () => {
  await fetchEvents()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar__select {
  width: 320px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
