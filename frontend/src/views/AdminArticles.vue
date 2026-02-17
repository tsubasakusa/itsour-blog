<template>
  <div class="admin-articles">
    <!-- 讀取中 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-text">LOADING...</p>
      </div>
    </div>

    <template v-else>
    <!-- 儀錶板 -->
    <div class="dashboard">
      <div class="stat-card">
        <h3>{{ stats.total_articles }}</h3>
        <p>總文章數</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.published_articles }}</h3>
        <p>已發布</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.draft_articles }}</h3>
        <p>草稿</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.total_views }}</h3>
        <p>總瀏覽</p>
      </div>
    </div>

    <button @click="reindex" class="action-btn">重新索引 Elasticsearch</button>
    <p v-if="message" class="message">{{ message }}</p>

    <!-- 文章管理 -->
    <div class="article-management">
      <button @click="openCreateForm" class="create-btn">+ 新增文章</button>

      <!-- 創建/編輯表單 -->
      <div v-if="showForm" class="form-modal" @click.self="cancelForm" @keydown.esc="cancelForm">
        <div class="form-content">
          <div class="form-header">
            <h3>{{ editingId ? '編輯文章' : '新增文章' }}</h3>
            <button @click="cancelForm" class="close-btn" title="取消">&times;</button>
          </div>

          <!-- 標題 -->
          <div class="field-group" :class="{ 'field-error': validationErrors.title }">
            <input v-model="form.title" placeholder="標題（必填）" />
            <span v-if="validationErrors.title" class="error-msg">{{ validationErrors.title }}</span>
          </div>

          <!-- 摘要 + AI 按鈕 -->
          <div class="summary-field">
            <input v-model="form.summary" placeholder="摘要（留空自動擷取）" />
            <button @click="generateSummary" class="ai-btn" :disabled="generatingSummary || !form.content" title="AI 生成摘要">
              {{ generatingSummary ? '...' : 'AI' }}
            </button>
          </div>

          <div class="form-row">
            <select v-model="form.category_id">
              <option :value="null">-- 選擇分類 --</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <input v-model="tagInput" placeholder="標籤（逗號分隔）" />
          </div>

          <TipTapEditor v-model="form.content" />

          <div class="form-row">
            <label><input type="checkbox" v-model="form.is_published" /> 發布</label>
            <label><input type="checkbox" v-model="form.featured" /> 精選</label>
          </div>

          <!-- 文章附圖管理 -->
          <div class="images-section">
            <div class="images-header">
              <span class="images-label">文章附圖</span>
            </div>
            <!-- 已有的圖片（編輯時） -->
            <div v-if="existingImages.length" class="preview-grid">
              <div v-for="img in existingImages" :key="'existing-' + img.id" class="preview-item">
                <img :src="getImageUrl(img.thumbnail_path || img.filepath)" :alt="img.alt_text || img.filename" />
                <button @click="deleteExistingImage(img.id)" class="preview-remove" title="刪除">&times;</button>
                <span class="preview-name">{{ img.filename }}</span>
              </div>
            </div>
            <!-- 新選擇的圖片 -->
            <div v-if="previews.length" class="preview-grid">
              <div v-for="(p, i) in previews" :key="'new-' + i" class="preview-item preview-new">
                <img :src="p.url" :alt="p.name" />
                <button @click="removeFile(i)" class="preview-remove" title="移除">&times;</button>
                <span class="preview-name">{{ p.name }}</span>
                <span class="preview-badge-new">NEW</span>
              </div>
            </div>
            <button @click="triggerFileInput" class="upload-images-btn">+ 上傳圖片</button>
            <input type="file" ref="fileInputRef" @change="handleFiles" multiple accept="image/*" hidden />
          </div>

          <!-- 儲存操作 -->
          <div class="form-actions">
            <button @click="saveArticle" class="save-btn" :disabled="saving">
              {{ saving ? '儲存中...' : '儲存' }}
            </button>
            <button @click="cancelForm" class="cancel-btn" :disabled="saving">取消</button>
          </div>

          <!-- 儲存訊息 -->
          <p v-if="saveMessage" :class="['save-msg', saveMessageType]">{{ saveMessage }}</p>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="article-table">
        <div v-for="article in articles" :key="article.id" class="article-row">
          <div class="article-info">
            <h4>{{ article.title }}</h4>
            <span class="badge">{{ getCategoryName(article.category_id) || 'MISC' }}</span>
            <span v-if="!article.is_published" class="draft-badge">草稿</span>
            <span v-if="article.featured" class="featured-badge">精選</span>
            <span class="reading-time">{{ article.reading_time || 1 }} 分鐘</span>
          </div>
          <div class="article-actions">
            <button @click="editArticle(article)" class="edit-btn" :disabled="loadingArticleId === article.id">
              {{ loadingArticleId === article.id ? '載入中...' : '編輯' }}
            </button>
            <button @click="deleteArticle(article.id)" class="delete-btn">刪除</button>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { articleAPI, categoryAPI, mediaAPI, aiAPI } from '../api'
import TipTapEditor from '../components/TipTapEditor.vue'

export default {
  components: { TipTapEditor },
  setup() {
    const loading = ref(true)
    const stats = ref({ total_articles: 0, published_articles: 0, draft_articles: 0, total_views: 0 })
    const articles = ref([])
    const categories = ref([])
    const showForm = ref(false)
    const editingId = ref(null)
    const message = ref('')
    const tagInput = ref('')
    const selectedFiles = ref([])
    const previews = ref([])
    const fileInputRef = ref(null)
    const saving = ref(false)
    const saveMessage = ref('')
    const saveMessageType = ref('success')
    const loadingArticleId = ref(null)
    const existingImages = ref([])
    const validationErrors = ref({})
    const generatingSummary = ref(false)

    const form = ref({
      title: '',
      content: '',
      summary: '',
      category_id: null,
      is_published: true,
      featured: false
    })

    const getImageUrl = (path) => {
      if (!path) return ''
      return `/uploads/${path.replace(/^uploads\//, '')}`
    }

    const stripHtml = (html) => html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()

    // === Data Loading ===
    const loadStats = async () => {
      try {
        const res = await articleAPI.getStats()
        stats.value = res.data
      } catch (e) { console.error(e) }
    }

    const loadArticles = async () => {
      try {
        const res = await articleAPI.getAll({ published_only: false })
        articles.value = res.data
      } catch (e) { console.error(e) }
    }

    const loadCategories = async () => {
      try {
        const res = await categoryAPI.getAll()
        categories.value = res.data
      } catch (e) { console.error(e) }
    }

    const getCategoryName = (catId) => {
      if (!catId) return null
      const cat = categories.value.find(c => c.id === catId)
      return cat ? cat.name : null
    }

    const reindex = async () => {
      message.value = '索引中...'
      try {
        const res = await articleAPI.reindex()
        message.value = res.data.message
      } catch (e) {
        message.value = '索引失敗'
      }
      setTimeout(() => message.value = '', 3000)
    }

    // === Form ===
    const openCreateForm = () => {
      cancelForm()
      showForm.value = true
    }

    const validate = () => {
      validationErrors.value = {}
      if (!form.value.title.trim()) {
        validationErrors.value.title = '請輸入標題'
      }
      return Object.keys(validationErrors.value).length === 0
    }

    // === Image Handling ===
    const triggerFileInput = () => {
      fileInputRef.value?.click()
    }

    const handleFiles = (e) => {
      const files = Array.from(e.target.files)
      for (const file of files) {
        selectedFiles.value.push(file)
        previews.value.push({ url: URL.createObjectURL(file), name: file.name })
      }
      if (fileInputRef.value) fileInputRef.value.value = ''
    }

    const removeFile = (index) => {
      URL.revokeObjectURL(previews.value[index].url)
      previews.value.splice(index, 1)
      selectedFiles.value.splice(index, 1)
    }

    const deleteExistingImage = async (imageId) => {
      if (!confirm('確定刪除此圖片？')) return
      try {
        await mediaAPI.delete(imageId)
        existingImages.value = existingImages.value.filter(img => img.id !== imageId)
      } catch (e) {
        console.error('Failed to delete image', e)
      }
    }

    // === Save ===
    const saveArticle = async () => {
      if (!validate()) return
      if (saving.value) return
      saving.value = true
      saveMessage.value = ''

      try {
        // Auto-generate summary if empty
        const summary = form.value.summary.trim()
          || stripHtml(form.value.content).substring(0, 150)
          || ''

        const data = {
          ...form.value,
          summary,
          tag_names: tagInput.value.split(',').map(t => t.trim()).filter(t => t)
        }

        let articleId = editingId.value

        if (editingId.value) {
          await articleAPI.update(editingId.value, data)
        } else {
          const res = await articleAPI.create(data)
          articleId = res.data.id
        }

        // Upload new images (both create and edit)
        for (const file of selectedFiles.value) {
          await articleAPI.uploadImage(articleId, file)
        }

        saveMessage.value = '儲存成功'
        saveMessageType.value = 'success'
        setTimeout(() => {
          cancelForm()
          loadArticles()
          loadStats()
        }, 600)
      } catch (e) {
        console.error('Save failed', e)
        saveMessage.value = e.response?.data?.detail || '儲存失敗，請重試'
        saveMessageType.value = 'error'
        saving.value = false
      }
    }

    // === AI Summary ===
    const generateSummary = async () => {
      if (!form.value.content || generatingSummary.value) return
      generatingSummary.value = true
      try {
        const text = stripHtml(form.value.content)
        const res = await aiAPI.generateSummary(text, form.value.title)
        if (res.data.summary) {
          form.value.summary = res.data.summary
        }
      } catch (e) {
        const detail = e.response?.data?.detail || 'AI 生成失敗'
        saveMessage.value = detail
        saveMessageType.value = 'error'
        setTimeout(() => saveMessage.value = '', 3000)
      } finally {
        generatingSummary.value = false
      }
    }

    // === Edit ===
    const editArticle = async (article) => {
      if (loadingArticleId.value) return
      loadingArticleId.value = article.id
      try {
        const res = await articleAPI.getOne(article.id)
        const full = res.data
        editingId.value = full.id
        form.value = {
          title: full.title,
          content: full.content || '',
          summary: full.summary || '',
          category_id: full.category_id || null,
          is_published: full.is_published,
          featured: full.featured,
        }
        tagInput.value = (full.tags || []).map(t => t.name).join(', ')
        existingImages.value = full.images || []
        showForm.value = true
      } catch (e) {
        console.error('Failed to load article', e)
      } finally {
        loadingArticleId.value = null
      }
    }

    const deleteArticle = async (id) => {
      if (confirm('確定刪除？')) {
        await articleAPI.delete(id)
        loadArticles()
        loadStats()
      }
    }

    const cancelForm = () => {
      showForm.value = false
      editingId.value = null
      form.value = { title: '', content: '', summary: '', category_id: null, is_published: true, featured: false }
      tagInput.value = ''
      previews.value.forEach(p => URL.revokeObjectURL(p.url))
      previews.value = []
      selectedFiles.value = []
      existingImages.value = []
      saving.value = false
      saveMessage.value = ''
      validationErrors.value = {}
    }

    // === Esc key handler ===
    const handleEsc = (e) => {
      if (e.key === 'Escape' && showForm.value) {
        cancelForm()
      }
    }

    onMounted(async () => {
      document.addEventListener('keydown', handleEsc)
      try {
        await Promise.all([loadStats(), loadArticles(), loadCategories()])
      } finally {
        loading.value = false
      }
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleEsc)
    })

    return {
      loading, stats, articles, categories, showForm, form, editingId, message, tagInput,
      previews, fileInputRef, saving, saveMessage, saveMessageType,
      loadingArticleId, existingImages, validationErrors, generatingSummary,
      reindex, openCreateForm, saveArticle, editArticle, deleteArticle, cancelForm,
      handleFiles, removeFile, triggerFileInput, deleteExistingImage,
      getCategoryName, getImageUrl, generateSummary,
    }
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

.loading-box {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #000;
  border-top-color: #FFC107;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 3px;
  color: #000;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #000;
  color: #FFC107;
  padding: 30px;
  text-align: center;
  border: 3px solid #FFC107;
  box-shadow: 5px 5px 0 #FFC107;
}

.stat-card h3 { font-size: 48px; margin-bottom: 10px; }

.action-btn {
  padding: 12px 24px;
  background: #000;
  color: #FFC107;
  border: 3px solid #FFC107;
  font-family: 'Courier New', monospace;
  cursor: pointer;
  margin-bottom: 20px;
  box-shadow: 4px 4px 0 #FFC107;
}

.action-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #FFC107;
}

.message {
  color: #00ff00;
  font-family: 'Courier New', monospace;
  margin-bottom: 20px;
}

.create-btn {
  padding: 12px 24px;
  background: #FFC107;
  color: #000;
  border: 3px solid #000;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 20px;
  box-shadow: 4px 4px 0 #000;
}

.form-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.form-content {
  background: #FFFBEA;
  padding: 40px;
  border: 6px solid #000;
  max-width: 800px;
  width: 95%;
  max-height: 95vh;
  overflow-y: auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-header h3 { font-size: 24px; }

.close-btn {
  background: none;
  border: 2px solid #000;
  font-size: 28px;
  line-height: 1;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Courier New', monospace;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #000;
  color: #FFC107;
}

/* Field validation */
.field-group {
  margin-bottom: 15px;
}

.field-group input {
  width: 100%;
  padding: 10px;
  border: 2px solid #000;
  font-family: inherit;
}

.field-error input {
  border-color: #f44336;
  background: #fff5f5;
}

.error-msg {
  display: block;
  color: #f44336;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  margin-top: 4px;
}

/* Summary + AI button */
.summary-field {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.summary-field input {
  flex: 1;
  padding: 10px;
  border: 2px solid #000;
  font-family: inherit;
}

.ai-btn {
  padding: 10px 16px;
  background: #000;
  color: #FFC107;
  border: 2px solid #FFC107;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.ai-btn:hover:not(:disabled) {
  background: #FFC107;
  color: #000;
}

.ai-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.form-content select {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 2px solid #000;
  font-family: inherit;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-row select,
.form-row input {
  flex: 1;
  margin-bottom: 0;
  padding: 10px;
  border: 2px solid #000;
  font-family: inherit;
}

.form-content label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-right: 15px;
  font-family: 'Courier New', monospace;
}

/* Images Section */
.images-section {
  margin-top: 15px;
  padding: 15px;
  border: 2px dashed #999;
  background: #fff;
}

.images-header {
  margin-bottom: 10px;
}

.images-label {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 1px;
}

.upload-images-btn {
  padding: 8px 16px;
  background: #fff;
  border: 2px solid #000;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-images-btn:hover {
  background: #FFC107;
}

.preview-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 2px solid #000;
  overflow: hidden;
}

.preview-new {
  border-color: #4caf50;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.preview-remove {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 22px;
  height: 22px;
  background: #000;
  color: #FFC107;
  border: none;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-remove:hover {
  background: #f44336;
  color: #fff;
}

.preview-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.7);
  color: #fff;
  font-size: 9px;
  font-family: 'Courier New', monospace;
  padding: 2px 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-badge-new {
  position: absolute;
  top: 2px;
  left: 2px;
  background: #4caf50;
  color: #fff;
  font-size: 8px;
  font-family: 'Courier New', monospace;
  padding: 1px 4px;
  font-weight: bold;
}

/* Save actions */
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.save-btn {
  padding: 10px 20px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
  font-family: 'Courier New', monospace;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 10px 20px;
  background: #ccc;
  border: none;
  cursor: pointer;
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-msg {
  margin-top: 12px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.save-msg.success {
  color: #4caf50;
}

.save-msg.error {
  color: #f44336;
}

/* Article table */
.article-table { margin-top: 30px; }

.article-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 2px solid #000;
  margin-bottom: 10px;
  background: #fff;
}

.article-info h4 { margin-bottom: 10px; }

.badge {
  display: inline-block;
  padding: 3px 8px;
  background: #FFC107;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  margin-right: 5px;
}

.draft-badge {
  display: inline-block;
  padding: 3px 8px;
  background: #ff9800;
  color: #fff;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  margin-right: 5px;
}

.featured-badge {
  display: inline-block;
  padding: 3px 8px;
  background: #000;
  color: #FFC107;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  margin-right: 5px;
}

.reading-time {
  font-size: 11px;
  font-family: 'Courier New', monospace;
  color: #666;
}

.article-actions { display: flex; gap: 10px; }

.edit-btn {
  padding: 8px 16px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
}

.edit-btn:disabled {
  opacity: 0.5;
  cursor: wait;
}

.delete-btn {
  padding: 8px 16px;
  background: #f44336;
  color: #fff;
  border: none;
  cursor: pointer;
}
</style>
