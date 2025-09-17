<template>
  <div class="layout">
    <header class="layout__header">
      <div class="brand">Top Scoot Admin</div>
      <ElMenu :default-active="activePath" mode="horizontal" class="layout__menu" @select="handleSelect">
        <ElMenuItem index="/admin/riders">Райдеры</ElMenuItem>
        <ElMenuItem index="/admin/events">Турниры</ElMenuItem>
        <ElMenuItem index="/admin/results">Результаты</ElMenuItem>
      </ElMenu>
      <div class="user-info">
        <span class="user-email">{{ auth.user?.email }}</span>
        <ElButton size="small" @click="handleLogout">Выйти</ElButton>
      </div>
    </header>
    <main class="layout__content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { logout, useAuthState } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthState()

const activePath = computed(() => {
  if (route.path.startsWith('/admin/results')) return '/admin/results'
  if (route.path.startsWith('/admin/events')) return '/admin/events'
  return '/admin/riders'
})

function handleSelect(path) {
  if (path !== route.path) {
    router.push(path)
  }
}

async function handleLogout() {
  await logout()
  router.replace({ name: 'admin-login' })
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #000;
  color: #fff;
  padding: 12px 24px;
  gap: 16px;
}

.brand {
  font-weight: 600;
  font-size: 18px;
}

.layout__menu {
  flex: 1;
  background: transparent;
}

.layout__menu :deep(.el-menu-item) {
  color: #fff;
}

.layout__menu :deep(.el-menu-item.is-active) {
  background-color: #E53935;
  color: #fff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
}

.user-email {
  font-size: 14px;
}

.layout__content {
  flex: 1;
  padding: 24px;
}
</style>
