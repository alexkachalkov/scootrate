<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h1 class="title">Top Scoot Admin</h1>
      <ElForm @submit.prevent="handleSubmit" :model="form" label-position="top">
        <ElFormItem label="Email">
          <ElInput v-model="form.email" type="email" autocomplete="email" />
        </ElFormItem>
        <ElFormItem label="Пароль">
          <ElInput v-model="form.password" type="password" autocomplete="current-password" show-password />
        </ElFormItem>
        <ElAlert v-if="auth.error" :title="auth.error" type="error" :closable="false" class="mb-3" />
        <ElButton type="primary" native-type="submit" :loading="auth.loading" block>
          Войти
        </ElButton>
      </ElForm>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login, ensureUser, useAuthState } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const form = reactive({
  email: '',
  password: ''
})
const auth = useAuthState()

onMounted(async () => {
  const user = await ensureUser()
  if (user) {
    router.replace({ name: 'admin-riders' })
  }
})

async function handleSubmit() {
  const { success } = await login({ ...form })
  if (success) {
    const redirect = route.query.redirect || '/admin'
    router.replace(redirect)
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #000000, #E53935);
  padding: 24px;
}

.login-card {
  background: #fff;
  padding: 32px;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  margin-bottom: 24px;
  color: #000;
}

.mb-3 {
  margin-bottom: 16px;
}
</style>
