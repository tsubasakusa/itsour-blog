<template>
  <div class="newspaper">
    <!-- 報頭 -->
    <header class="masthead">
      <div class="meta-info">
        <span>伺服器狀態：運行中 ●</span>
        <span>{{ new Date().toLocaleDateString('zh-TW') }}</span>
        <span>穩定度：99.9%</span>
      </div>
      <h1 class="title">日常遷移</h1>
      <div class="subtitle">DAILY MIGRATION</div>
      <div class="divider"></div>
    </header>

    <!-- 導覽列 -->
    <nav class="nav">
      <router-link to="/" class="nav-link tab-trivial" exact-active-class="active">瑣事</router-link>
      <router-link to="/about" class="nav-link tab-people" active-class="active">人</router-link>
    </nav>

    <!-- 主要內容 -->
    <main>
      <router-view />
    </main>

    <GrainOverlay />
  </div>
</template>

<script>
import GrainOverlay from '../components/GrainOverlay.vue'

export default {
  components: { GrainOverlay },
}
</script>

<style scoped>
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
  padding: 0 40px;
  display: flex;
  gap: 0;
}

.nav-link {
  color: #FFC107;
  text-decoration: none;
  font-family: 'Courier New', monospace;
  font-size: 16px;
  letter-spacing: 3px;
  padding: 16px 28px;
  border-bottom: 4px solid transparent;
  transition: all 0.3s;
}

.nav-link:hover {
  color: #fff;
}

.tab-trivial.active {
  color: #fff;
  border-bottom: 4px solid #000;
  background: rgba(255, 255, 255, 0.05);
}

.tab-people.active {
  color: #fff;
  border-bottom: 4px solid #f44336;
  background: rgba(255, 255, 255, 0.05);
}

main {
  padding: 40px;
}
</style>
