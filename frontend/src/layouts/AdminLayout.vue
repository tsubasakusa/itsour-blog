<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="header-left">
        <h1 class="admin-title">[ ADMIN_PANEL ]</h1>
      </div>
      <nav class="admin-nav">
        <router-link to="/plague" exact-active-class="active" class="nav-item">文章管理</router-link>
        <router-link to="/plague/categories" active-class="active" class="nav-item">分類管理</router-link>
        <router-link to="/plague/media" active-class="active" class="nav-item">媒體庫</router-link>
        <router-link to="/" class="nav-item nav-home">首頁</router-link>
        <a href="#" @click.prevent="handleLogout" class="nav-item nav-logout">登出</a>
      </nav>
    </header>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { authAPI } from '../api'

export default {
  setup() {
    const router = useRouter()

    const handleLogout = () => {
      authAPI.logout()
      router.push('/plague/login')
    }

    return { handleLogout }
  }
}
</script>

<style scoped>
.admin-layout {
  max-width: 1200px;
  margin: 0 auto;
  background: #FFFBEA;
  min-height: 100vh;
  box-shadow: 0 0 50px rgba(0,0,0,0.3);
}

.admin-header {
  background: #000;
  padding: 20px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
}

.admin-title {
  font-family: 'Courier New', monospace;
  font-size: 24px;
  color: #FFC107;
  letter-spacing: 3px;
}

.admin-nav {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-item {
  color: #FFC107;
  text-decoration: none;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 1px;
  padding: 8px 16px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover {
  border-color: #FFC107;
}

.nav-item.active {
  background: #FFC107;
  color: #000;
  font-weight: bold;
}

.nav-home {
  color: #aaa;
}

.nav-logout {
  color: #ff5252;
}

.nav-logout:hover {
  border-color: #ff5252;
}

.admin-main {
  padding: 40px;
}
</style>
