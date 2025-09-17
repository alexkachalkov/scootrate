<template>
  <div class="section">
    <div class="container">
      <h1>Предложить турнир</h1>
      <p>Если вы организуете контест и хотите попасть в рейтинг, заполните форму. Мы проверим данные и свяжемся с вами.</p>

      <ElForm :model="form" label-position="top" class="form" @submit.prevent>
        <ElFormItem label="Название турнира" required>
          <ElInput v-model="form.name" placeholder="Название" />
        </ElFormItem>
        <ElFormItem label="Дата" required>
          <ElDatePicker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="Выберите дату" />
        </ElFormItem>
        <ElFormItem label="Город" required>
          <ElInput v-model="form.city" placeholder="Где проходит" />
        </ElFormItem>
        <ElFormItem label="Уровень" required>
          <ElSelect v-model="form.level" placeholder="Выберите уровень">
            <ElOption label="Локальный" value="local" />
            <ElOption label="Региональный" value="regional" />
            <ElOption label="Национальный" value="national" />
            <ElOption label="Международный" value="international" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="Ссылка на источник" required>
          <ElInput v-model="form.link" placeholder="Например, страница мероприятия или гугл-таблица" />
        </ElFormItem>
        <ElFormItem label="CSV протокол (опционально)">
          <ElUpload
            class="upload"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept=".csv"
          >
            <ElButton>Загрузить CSV</ElButton>
            <span class="upload__filename" v-if="form.fileName">{{ form.fileName }}</span>
          </ElUpload>
        </ElFormItem>
        <ElFormItem label="Контакты организатора" required>
          <ElInput v-model="form.contact" type="textarea" rows="3" placeholder="Email и/или телефон" />
        </ElFormItem>
        <ElFormItem label="Комментарий">
          <ElInput v-model="form.comment" type="textarea" rows="3" placeholder="Дополнительные сведения" />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" :loading="sending" @click="submit">Отправить</ElButton>
          <ElButton @click="reset">Сбросить</ElButton>
        </ElFormItem>
      </ElForm>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElNotification } from 'element-plus'

const sending = ref(false)
const form = reactive({
  name: '',
  date: '',
  city: '',
  level: '',
  link: '',
  contact: '',
  comment: '',
  file: null,
  fileName: ''
})

function handleFileChange(upload) {
  const file = upload.raw
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElNotification.error({ title: 'Ошибка', message: 'Файл больше 2 МБ' })
    return
  }
  form.file = file
  form.fileName = file.name
}

function reset() {
  form.name = ''
  form.date = ''
  form.city = ''
  form.level = ''
  form.link = ''
  form.contact = ''
  form.comment = ''
  form.file = null
  form.fileName = ''
}

async function submit() {
  if (!form.name || !form.date || !form.city || !form.level || !form.link || !form.contact) {
    ElNotification.warning({ title: 'Проверьте форму', message: 'Заполните обязательные поля' })
    return
  }
  sending.value = true
  try {
    // Пока простое логирование. В бою здесь будет вызов API.
    console.info('[Top Scoot] tournament submission', { ...form, file: form.file ? form.file.name : null })
    await new Promise((resolve) => setTimeout(resolve, 600))
    ElNotification.success({ title: 'Спасибо!', message: 'Мы получили заявку и скоро свяжемся с вами.' })
    reset()
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.section {
  padding: 50px 0 80px;
  background: #fff;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 24px;
  line-height: 1.6;
}

.form {
  margin-top: 24px;
}

.upload {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload__filename {
  font-size: 13px;
  color: #555;
}
</style>
