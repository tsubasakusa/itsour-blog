<template>
  <div class="admin-panel">
    <h2 class="section-title">[ ADMIN_PANEL ]</h2>
    
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

    <button @click="reindex" class="action-btn">🔄 重新索引 Elasticsearch</button>
    <p v-if="message" class="message">{{ message }}</p>

    <!-- 文章管理 -->
    <div class="article-management">
      <button @click="showForm = true" class="create-btn">+ 新增文章</button>

      <!-- 創建/編輯表單 -->
      <div v-if="showForm" class="form-modal">
        <div class="form-content">
          <h3>{{ editingId ? '編輯文章' : '新增文章' }}</h3>
          <input v-model="form.title" placeholder="標題" />
          <textarea v-model="form.content" placeholder="內容" rows="8"></textarea>
          <input v-model="form.summary" placeholder="摘要（選填）" />
          <input v-model="form.category" placeholder="分類 (如: Python, Docker)" />
          <input v-model="tagInput" placeholder="標籤（逗號分隔）" />
          <label><input type="checkbox" v-model="form.is_published" /> 發布</label>
          <label><input type="checkbox" v-model="form.featured" /> 精選</label>
          <input type="file" @change="handleFiles" multiple accept="image/*" />
          <div class="form-actions">
            <button @click="saveArticle" class="save-btn">儲存</button>
            <button @click="cancelForm" class="cancel-btn">取消</button>
          </div>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="article-table">
        <div v-for="article in articles" :key="article.id" class="article-row">
          <div class="article-info">
            <h4>{{ article.title }}</h4>
            <span class="badge">{{ article.category || 'MISC' }}</span>
            <span v-if="!article.is_published" class="draft-badge">草稿</span>
            <span v-if="article.featured" class="featured-badge">精選</span>
          </div>
          <div class="article-actions">
            <button @click="editArticle(article)" class="edit-btn">編輯</button>
            <button @click="deleteArticle(article.id)" class="delete-btn">刪除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { articleAPI } from '../api'

export default {
  setup() {
    const stats = ref({ total_articles: 0, published_articles: 0, draft_articles: 0, total_views: 0 })
    const articles = ref([])
    const showForm = ref(false)
    const editingId = ref(null)
    const message = ref('')
    const tagInput = ref('')
    const selectedFiles = ref([])
    
    const form = ref({
      title: '',
      content: '',
      summary: '',
      category: '',
      is_published: true,
      featured: false
    })

    const loadStats = async () => {
      const res = await articleAPI.getStats()
      stats.value = res.data
    }

    const loadArticles = async () => {
      const res = await articleAPI.getAll({ published_only: false })
      articles.value = res.data
    }

    const reindex = async () => {
      message.value = '索引中...'
      const res = await articleAPI.reindex()
      message.value = res.data.message
      setTimeout(() => message.value = '', 3000)
    }

    const handleFiles = (e) => {
      selectedFiles.value = Array.from(e.target.files)
    }

    const saveArticle = async () => {
      const data = {
        ...form.value,
        tag_names: tagInput.value.split(',').map(t => t.trim()).filter(t => t)
      }

      if (editingId.value) {
        await articleAPI.update(editingId.value, data)
      } else {
        const res = await articleAPI.create(data)
        const articleId = res.data.id
        
        for (const file of selectedFiles.value) {
          await articleAPI.uploadImage(articleId, file)
        }
      }

      cancelForm()
      loadArticles()
      loadStats()
    }

    const editArticle = (article) => {
      editingId.value = article.id
      form.value = { ...article }
      tagInput.value = article.tags.map(t => t.name).join(', ')
      showForm.value = true
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
      form.value = { title: '', content: '', summary: '', category: '', is_published: true, featured: false }
      tagInput.value = ''
      selectedFiles.value = []
    }

    onMounted(() => {
      loadStats()
      loadArticles()
    })

    return { stats, articles, showForm, form, editingId, message, tagInput, reindex, saveArticle, editArticle, deleteArticle, cancelForm, handleFiles }
  }
}
</script>

<style scoped>
.section-title {
  font-family: 'Courier New', monospace;
  font-size: 28px;
  margin-bottom: 30px;
  letter-spacing: 3px;
  border-left: 6px solid #000;
  padding-left: 15px;
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

.stat-card h3 {
  font-size: 48px;
  margin-bottom: 10px;
}

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
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.form-content h3 {
  margin-bottom: 20px;
  font-size: 24px;
}

.form-content input,
.form-content textarea {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 2px solid #000;
  font-family: inherit;
}

.form-content label {
  display: block;
  margin-bottom: 10px;
  font-family: 'Courier New', monospace;
}

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
}

.cancel-btn {
  padding: 10px 20px;
  background: #ccc;
  border: none;
  cursor: pointer;
}

.article-table {
  margin-top: 30px;
}

.article-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 2px solid #000;
  margin-bottom: 10px;
  background: #fff;
}

.article-info h4 {
  margin-bottom: 10px;
}

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
}

.article-actions {
  display: flex;
  gap: 10px;
}

.edit-btn {
  padding: 8px 16px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
}

.delete-btn {
  padding: 8px 16px;
  background: #f44336;
  color: #fff;
  border: none;
  cursor: pointer;
}
</style>
