<template>
  <div class="article-list">
    <h2>文章列表</h2>
    <div class="toolbar">
      <div class="search-box">
        <input v-model="searchQuery" @input="handleSearch" placeholder="🔍 搜尋文章標題、內容或作者..." />
        <button v-if="searchQuery" @click="clearSearch" class="clear-btn">清除</button>
      </div>
      <button @click="showCreateForm = true" class="create-btn">+ 新增文章</button>
    </div>
    <p v-if="searchQuery" class="search-info">搜尋結果: "{{ searchQuery }}" ({{ articles.length }} 篇)</p>
    
    <div v-if="showCreateForm" class="form">
      <h3>新增文章</h3>
      <input v-model="newArticle.title" placeholder="標題" />
      <textarea v-model="newArticle.content" placeholder="內容"></textarea>
      <input v-model="newArticle.author" placeholder="作者" />
      <input type="file" @change="handleFileSelect" accept="image/*" multiple />
      <button @click="createArticle">儲存</button>
      <button @click="showCreateForm = false">取消</button>
    </div>

    <div v-for="article in articles" :key="article.id" class="article">
      <h3>{{ article.title }}</h3>
      <p>{{ article.content }}</p>
      <div v-if="article.images.length" class="images">
        <img v-for="img in article.images" :key="img.id" :src="`/uploads/${img.filename}`" />
      </div>
      <small>作者: {{ article.author }} | {{ new Date(article.created_at).toLocaleString() }}</small>
      <div>
        <button @click="deleteArticle(article.id)">刪除</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { articleAPI } from '../api'

export default {
  setup() {
    const articles = ref([])
    const showCreateForm = ref(false)
    const newArticle = ref({ title: '', content: '', author: '' })
    const searchQuery = ref('')
    const selectedFiles = ref([])

    const loadArticles = async () => {
      const res = await articleAPI.getAll()
      articles.value = res.data
    }

    const handleSearch = async () => {
      if (searchQuery.value.trim()) {
        const res = await articleAPI.search(searchQuery.value)
        articles.value = res.data
      } else {
        loadArticles()
      }
    }

    const handleFileSelect = (e) => {
      selectedFiles.value = Array.from(e.target.files)
    }

    const createArticle = async () => {
      const res = await articleAPI.create(newArticle.value)
      const articleId = res.data.id
      
      for (const file of selectedFiles.value) {
        await articleAPI.uploadImage(articleId, file)
      }
      
      newArticle.value = { title: '', content: '', author: '' }
      selectedFiles.value = []
      showCreateForm.value = false
      loadArticles()
    }

    const deleteArticle = async (id) => {
      if (confirm('確定要刪除嗎？')) {
        await articleAPI.delete(id)
        loadArticles()
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      loadArticles()
    }

    onMounted(loadArticles)

    return { articles, showCreateForm, newArticle, searchQuery, createArticle, deleteArticle, handleSearch, handleFileSelect, clearSearch }
  }
}
</script>

<style scoped>
.article-list { max-width: 800px; margin: 0 auto; padding: 20px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 20px; align-items: center; }
.search-box { flex: 1; display: flex; gap: 5px; position: relative; }
.search-box input { 
  flex: 1; 
  padding: 12px 15px; 
  border: 2px solid #4CAF50; 
  border-radius: 8px; 
  font-size: 16px;
  outline: none;
}
.search-box input:focus { border-color: #45a049; box-shadow: 0 0 5px rgba(76, 175, 80, 0.3); }
.clear-btn { 
  padding: 8px 12px; 
  background: #f44336; 
  color: white; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer; 
}
.create-btn { 
  padding: 12px 20px; 
  background: #4CAF50; 
  color: white; 
  border: none; 
  border-radius: 8px; 
  font-weight: bold; 
  cursor: pointer; 
}
.create-btn:hover { background: #45a049; }
.search-info { 
  background: #e3f2fd; 
  padding: 10px; 
  border-radius: 6px; 
  margin-bottom: 15px; 
  color: #1976d2; 
  font-weight: bold;
}
.form { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
.form input, .form textarea { width: 100%; margin: 10px 0; padding: 8px; }
.form textarea { min-height: 100px; }
.article { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 8px; }
.images { display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }
.images img { width: 150px; height: 150px; object-fit: cover; border-radius: 4px; }
button { padding: 8px 16px; margin: 5px; cursor: pointer; }
</style>
