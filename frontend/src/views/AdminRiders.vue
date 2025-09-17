<template>
  <div>
    <div class="toolbar">
      <ElInput
        v-model="filters.search"
        placeholder="Поиск по нику или имени"
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
        <ElOption label="Новичок" value="novice" />
        <ElOption label="Любитель" value="amateur" />
        <ElOption label="Про" value="pro" />
      </ElSelect>
      <ElSelect v-model="filters.style" placeholder="Стиль" clearable class="toolbar__select" @change="refresh">
        <ElOption label="Street" value="street" />
        <ElOption label="Park" value="park" />
        <ElOption label="Universal" value="universal" />
      </ElSelect>
      <ElButton type="primary" @click="openCreate" :icon="Plus">Добавить</ElButton>
    </div>

    <ElTable :data="items" v-loading="loading" height="550" stripe>
      <ElTableColumn prop="nickname" label="Ник" width="160" />
      <ElTableColumn prop="fullname" label="Имя" min-width="200" />
      <ElTableColumn prop="city" label="Город" width="150" />
      <ElTableColumn prop="level" label="Уровень" width="120" />
      <ElTableColumn prop="style" label="Стиль" width="120" />
      <ElTableColumn prop="birthdate" label="Дата рождения" width="150" />
      <ElTableColumn prop="email" label="Email" min-width="200" />
      <ElTableColumn label="Действия" width="150" fixed="right">
        <template #default="scope">
          <ElButton size="small" :icon="Edit" @click="openEdit(scope.row)"></ElButton>
          <ElButton
            size="small"
            type="danger"
            :icon="Delete"
            @click="confirmDelete(scope.row)"
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

    <ElDialog v-model="dialog.visible" :title="dialog.title" width="520px">
      <ElForm :model="form" label-position="top" :disabled="dialog.saving">
        <ElFormItem label="Никнейм" required>
          <ElInput v-model="form.nickname" />
        </ElFormItem>
        <ElFormItem label="Полное имя">
          <ElInput v-model="form.fullname" />
        </ElFormItem>
        <ElFormItem label="Город" required>
          <ElInput v-model="form.city" />
        </ElFormItem>
        <ElFormItem label="Дата рождения" required>
          <ElDatePicker
            v-model="form.birthdate"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            placeholder="YYYY-MM-DD"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="Стиль" required>
          <ElSelect v-model="form.style" placeholder="Выберите стиль">
            <ElOption label="Street" value="street" />
            <ElOption label="Park" value="park" />
            <ElOption label="Universal" value="universal" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Уровень" required>
          <ElSelect v-model="form.level" placeholder="Выберите уровень">
            <ElOption label="Новичок" value="novice" />
            <ElOption label="Любитель" value="amateur" />
            <ElOption label="Про" value="pro" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Email">
          <ElInput v-model="form.email" />
        </ElFormItem>
        <ElFormItem label="Фото URL">
          <ElInput v-model="form.photoUrl" />
        </ElFormItem>
        <ElFormItem label="Соцсети (JSON)">
          <ElInput v-model="form.socialsJson" type="textarea" rows="3" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <div class="dialog-footer">
          <ElButton @click="dialog.visible = false">Отмена</ElButton>
          <ElButton type="primary" :loading="dialog.saving" @click="saveRider">Сохранить</ElButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import api from '../api'

const items = ref([])
const loading = ref(false)
const filters = reactive({
  search: '',
  city: '',
  level: '',
  style: ''
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
  nickname: '',
  fullname: '',
  city: '',
  birthdate: '',
  style: '',
  level: '',
  email: '',
  photoUrl: '',
  socialsJson: '{}'
})

async function fetchRiders() {
  loading.value = true
  try {
    const params = {
      ...filters,
      page: pagination.page,
      limit: pagination.limit
    }
    const response = await api.get('/api/admin/riders', { params })
    items.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElNotification.error({
      title: 'Ошибка',
      message: 'Не удалось загрузить список райдеров'
    })
  } finally {
    loading.value = false
  }
}

function refresh() {
  pagination.page = 1
  fetchRiders()
}

function handlePageChange(page) {
  pagination.page = page
  fetchRiders()
}

function resetForm() {
  form.id = null
  form.nickname = ''
  form.fullname = ''
  form.city = ''
  form.birthdate = ''
  form.style = ''
  form.level = ''
  form.email = ''
  form.photoUrl = ''
  form.socialsJson = '{}'
}

function openCreate() {
  resetForm()
  dialog.title = 'Новый райдер'
  dialog.visible = true
}

function openEdit(row) {
  resetForm()
  form.id = row.id
  form.nickname = row.nickname
  form.fullname = row.fullname || ''
  form.city = row.city || ''
  form.birthdate = row.birthdate || ''
  form.style = row.style || ''
  form.level = row.level || ''
  form.email = row.email || ''
  form.photoUrl = row.photoUrl || ''
  form.socialsJson = row.socialsJson || '{}'
  dialog.title = 'Редактировать райдера'
  dialog.visible = true
}

async function saveRider() {
  dialog.saving = true
  try {
    const payload = {
      nickname: form.nickname,
      fullname: form.fullname,
      city: form.city,
      birthdate: form.birthdate,
      style: form.style,
      level: form.level,
      email: form.email,
      photoUrl: form.photoUrl,
      socialsJson: form.socialsJson
    }
    if (form.id) {
      await api.put(`/api/admin/riders/${form.id}`, payload)
      ElNotification.success({ title: 'Сохранено', message: 'Райдер обновлён' })
    } else {
      await api.post('/api/admin/riders', payload)
      ElNotification.success({ title: 'Создано', message: 'Райдер добавлен' })
    }
    dialog.visible = false
    fetchRiders()
  } catch (error) {
    const message = error?.response?.data?.errors?.join(', ') || 'Не удалось сохранить данные'
    ElNotification.error({ title: 'Ошибка', message })
  } finally {
    dialog.saving = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Удалить райдера «${row.nickname}»?`,
      'Подтверждение',
      {
        type: 'warning',
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
      }
    )
    await api.delete(`/api/admin/riders/${row.id}`)
    ElNotification.success({ title: 'Удалено', message: 'Райдер удалён' })
    fetchRiders()
  } catch (error) {
    if (error !== 'cancel') {
      const message = error?.response?.data?.error || 'Не удалось удалить райдера'
      ElNotification.error({ title: 'Ошибка', message })
    }
  }
}

onMounted(() => {
  fetchRiders()
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
  width: 180px;
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
