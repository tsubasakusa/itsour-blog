<template>
  <div class="login-page">
    <div class="login-box">
      <h2>[ ADMIN_LOGIN ]</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="username" type="text" placeholder="帳號" required />
        <input v-model="password" type="password" placeholder="密碼" required />
        <button type="submit">登入</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
      <p class="hint">預設：admin / admin123</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { authAPI } from '../api'

export default {
  emits: ['login-success'],
  setup(props, { emit }) {
    const username = ref('')
    const password = ref('')
    const error = ref('')

    const handleLogin = async () => {
      try {
        error.value = ''
        const res = await authAPI.login(username.value, password.value)
        localStorage.setItem('token', res.data.access_token)
        emit('login-success')
      } catch (err) {
        error.value = err.response?.data?.detail || '登入失敗'
      }
    }

    return { username, password, error, handleLogin }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFC107;
}

.login-box {
  background: #FFFBEA;
  padding: 60px;
  border: 6px solid #000;
  box-shadow: 12px 12px 0 #000;
  max-width: 400px;
  width: 90%;
}

.login-box h2 {
  font-family: 'Courier New', monospace;
  font-size: 28px;
  margin-bottom: 30px;
  text-align: center;
  letter-spacing: 3px;
}

.login-box input {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 3px solid #000;
  font-size: 16px;
  font-family: 'Courier New', monospace;
}

.login-box input:focus {
  outline: none;
  background: #FFC107;
}

.login-box button {
  width: 100%;
  padding: 15px;
  background: #000;
  color: #FFC107;
  border: none;
  font-size: 18px;
  font-family: 'Courier New', monospace;
  cursor: pointer;
  letter-spacing: 2px;
}

.login-box button:hover {
  background: #FFC107;
  color: #000;
  border: 3px solid #000;
}

.error {
  color: #f44336;
  margin-top: 15px;
  text-align: center;
  font-family: 'Courier New', monospace;
}

.hint {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #666;
  font-family: 'Courier New', monospace;
}
</style>
