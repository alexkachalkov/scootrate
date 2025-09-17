<template>
  <div class="layout">
    <header class="header">
      <div class="container header__inner">
        <RouterLink to="/" class="logo">Top Scoot</RouterLink>
        <nav class="nav">
          <RouterLink to="/rating" class="nav__link">Рейтинг</RouterLink>
          <RouterLink to="/events" class="nav__link">Турниры</RouterLink>
          <RouterLink to="/about" class="nav__link">Как работает</RouterLink>
          <RouterLink to="/rules" class="nav__link">Правила</RouterLink>
          <RouterLink to="/contact" class="nav__link">Контакты</RouterLink>
        </nav>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
    <footer class="footer">
      <div class="container footer__inner">
        <p>© {{ new Date().getFullYear() }} Top Scoot. Все права защищены.</p>
        <RouterLink to="/admin/login" class="footer__link">Вход для админов</RouterLink>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fdfdfd;
}

.header {
  background: #000;
  color: #fff;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.header__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  text-decoration: none;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav__link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  position: relative;
}

.nav__link.router-link-active::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -8px;
  width: 100%;
  height: 2px;
  background: #E53935;
}

.main {
  flex: 1;
}

.footer {
  background: #111;
  color: #fff;
  padding: 20px 0;
}

.footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.footer__link {
  color: #fff;
  text-decoration: none;
}

@media (max-width: 768px) {
  .header__inner {
    flex-direction: column;
    gap: 12px;
    height: auto;
    padding: 16px 0;
  }
  .nav {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
