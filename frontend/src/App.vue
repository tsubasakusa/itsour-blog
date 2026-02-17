<template>
  <div class="newspaper">
    <!-- 報頭 -->
    <header class="masthead">
      <div class="meta-info">
        <span>伺服器狀態：運行中 ●</span>
        <span>{{ new Date().toLocaleDateString('zh-TW') }}</span>
        <span>穩定度：99.9%</span>
      </div>
      <h1 class="title">ITSOUR PORTFOLIO</h1>
      <div class="subtitle">技術週刊 / TECHNICAL WEEKLY</div>
      <div class="divider"></div>
    </header>

    <!-- 導覽列 -->
    <nav class="nav">
      <a href="#" @click.prevent="view='home'" :class="{active: view==='home'}">首頁_HOME</a>
      <a href="#" @click.prevent="goToAdmin" :class="{active: view==='admin'}">管理_ADMIN</a>
      <a href="/docs" target="_blank">API_DOCS</a>
      <a v-if="isLoggedIn" href="#" @click.prevent="handleLogout" class="logout">登出_LOGOUT</a>
    </nav>

    <!-- 主要內容 -->
    <main v-if="view === 'home'">
      <FrontPage />
    </main>
    <main v-else-if="view === 'login'">
      <LoginPage @login-success="onLoginSuccess" />
    </main>
    <main v-else-if="view === 'admin' && isLoggedIn">
      <AdminPanel />
    </main>

    <GrainOverlay />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import FrontPage from './components/FrontPage.vue'
import AdminPanel from './components/AdminPanel.vue'
import LoginPage from './components/LoginPage.vue'
import GrainOverlay from './components/GrainOverlay.vue'
import { authAPI } from './api'

export default {
  components: { FrontPage, AdminPanel, LoginPage, GrainOverlay },
  setup() {
    const view = ref('home')
    const isLoggedIn = computed(() => !!localStorage.getItem('token'))

    const goToAdmin = () => {
      if (isLoggedIn.value) {
        view.value = 'admin'
      } else {
        view.value = 'login'
      }
    }

    const onLoginSuccess = () => {
      view.value = 'admin'
    }

    const handleLogout = () => {
      authAPI.logout()
      view.value = 'home'
    }

    return { view, isLoggedIn, goToAdmin, onLoginSuccess, handleLogout }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: #FFC107;
  font-family: 'Georgia', 'Times New Roman', serif;
  color: #000;
}

.newspaper {
  max-width: 1200px;
  margin: 0 auto;
  background: #FFFBEA;
  min-height: 100vh;
  box-shadow: 0 0 50px rgba(0,0,0,0.3);
}

.masthead {
  border-bottom: 6px double #000;
  border-top: 6px double #000;
  padding: 30px 40px;
  background: #FFC107;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 15px;
  font-family: 'Courier New', monospace;
}

.meta-info span:first-child::before {
  content: '●';
  color: #00ff00;
  animation: blink 2s infinite;
  margin-right: 5px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.masthead .title {
  font-size: 72px;
  font-weight: 900;
  text-align: center;
  letter-spacing: 8px;
  line-height: 1;
  text-shadow: 4px 4px 0 #000;
}

.masthead .subtitle {
  text-align: center;
  font-size: 14px;
  letter-spacing: 4px;
  margin-top: 10px;
  font-family: 'Courier New', monospace;
}

.divider {
  height: 2px;
  background: #000;
  margin-top: 20px;
}

.nav {
  background: #000;
  padding: 15px 40px;
  display: flex;
  gap: 30px;
}

.nav a {
  color: #FFC107;
  text-decoration: none;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 2px;
  transition: all 0.3s;
}

.nav a:hover,
.nav a.active {
  text-decoration: line-through;
  color: #fff;
}

.nav a.logout {
  margin-left: auto;
  color: #ff5252;
}

main {
  padding: 40px;
}
</style>
