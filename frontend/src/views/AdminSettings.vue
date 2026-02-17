<template>
  <div class="admin-settings">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-text">LOADING...</p>
      </div>
    </div>

    <template v-else>
      <h2 class="page-title">AI 設定</h2>

      <div class="settings-form">
        <div class="field">
          <label>API Base URL</label>
          <input v-model="form.ai_base_url" placeholder="https://api.openai.com/v1" />
          <span class="hint">支援 OpenAI 相容 API（OpenAI、Anthropic via proxy、Ollama 等）</span>
        </div>

        <div class="field">
          <label>API Key</label>
          <div class="key-field">
            <input
              v-model="form.ai_api_key"
              :type="showKey ? 'text' : 'password'"
              placeholder="sk-..."
            />
            <button @click="showKey = !showKey" class="toggle-key">{{ showKey ? 'HIDE' : 'SHOW' }}</button>
          </div>
        </div>

        <div class="field">
          <label>模型名稱</label>
          <input v-model="form.ai_model" placeholder="gpt-4o-mini" />
        </div>

        <div class="field">
          <label>摘要 Prompt</label>
          <textarea v-model="form.ai_summary_prompt" rows="4" placeholder="生成摘要的系統 prompt..."></textarea>
        </div>

        <div class="actions">
          <button @click="saveSettings" class="save-btn" :disabled="saving">
            {{ saving ? '儲存中...' : '儲存設定' }}
          </button>
        </div>

        <p v-if="message" :class="['msg', messageType]">{{ message }}</p>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { settingsAPI } from '../api'

export default {
  setup() {
    const loading = ref(true)
    const saving = ref(false)
    const showKey = ref(false)
    const message = ref('')
    const messageType = ref('success')

    const form = ref({
      ai_api_key: '',
      ai_model: '',
      ai_base_url: '',
      ai_summary_prompt: '',
    })

    const loadSettings = async () => {
      try {
        const res = await settingsAPI.getAll()
        form.value = {
          ai_api_key: '',
          ai_model: res.data.ai_model,
          ai_base_url: res.data.ai_base_url,
          ai_summary_prompt: res.data.ai_summary_prompt,
        }
      } catch (e) {
        console.error(e)
      }
    }

    const saveSettings = async () => {
      if (saving.value) return
      saving.value = true
      message.value = ''
      try {
        const data = { ...form.value }
        // Don't send empty api_key (preserve existing)
        if (!data.ai_api_key) {
          delete data.ai_api_key
        }
        await settingsAPI.update(data)
        message.value = '設定已儲存'
        messageType.value = 'success'
        // Clear the key field after save
        form.value.ai_api_key = ''
      } catch (e) {
        message.value = e.response?.data?.detail || '儲存失敗'
        messageType.value = 'error'
      } finally {
        saving.value = false
        setTimeout(() => message.value = '', 3000)
      }
    }

    onMounted(async () => {
      try {
        await loadSettings()
      } finally {
        loading.value = false
      }
    })

    return { loading, saving, showKey, message, messageType, form, saveSettings }
  }
}
</script>

<style scoped>
.loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-box { text-align: center; }

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #000;
  border-top-color: #FFC107;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 3px;
}

.page-title {
  font-family: 'Courier New', monospace;
  font-size: 22px;
  letter-spacing: 2px;
  margin-bottom: 30px;
  border-left: 6px solid #000;
  padding-left: 15px;
}

.settings-form {
  max-width: 600px;
}

.field {
  margin-bottom: 20px;
}

.field label {
  display: block;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.field input,
.field textarea {
  width: 100%;
  padding: 10px;
  border: 2px solid #000;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  background: #fff;
}

.field textarea {
  resize: vertical;
  line-height: 1.5;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #FFC107;
}

.hint {
  display: block;
  font-size: 11px;
  color: #888;
  font-family: 'Courier New', monospace;
  margin-top: 4px;
}

.key-field {
  display: flex;
  gap: 8px;
}

.key-field input {
  flex: 1;
}

.toggle-key {
  padding: 10px 14px;
  background: #000;
  color: #FFC107;
  border: 2px solid #000;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
}

.toggle-key:hover {
  background: #FFC107;
  color: #000;
}

.actions {
  margin-top: 25px;
}

.save-btn {
  padding: 12px 24px;
  background: #000;
  color: #FFC107;
  border: none;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  cursor: pointer;
  letter-spacing: 1px;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn:hover:not(:disabled) {
  background: #FFC107;
  color: #000;
  border: 2px solid #000;
}

.msg {
  margin-top: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.msg.success { color: #4caf50; }
.msg.error { color: #f44336; }
</style>
