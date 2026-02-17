<template>
  <div class="front-page">
    <!-- 搜尋欄 -->
    <div class="search-section">
      <input 
        v-model="searchQuery" 
        @input="handleSearch" 
        placeholder="搜尋文章、專案、技術..." 
        class="search-input"
      />
    </div>

    <!-- 精選文章 -->
    <section v-if="!searchQuery && featuredArticles.length" class="featured">
      <h2 class="section-title">[ FEATURED_POSTS ]</h2>
      <div class="featured-grid">
        <article 
          v-for="article in featuredArticles" 
          :key="article.id"
          @click="viewArticle(article.id)"
          class="featured-card"
        >
          <div class="image-wrapper">
            <div v-if="!article.images || !article.images[0]" class="placeholder-img">NO IMAGE</div>
            <img v-else :src="`http://localhost:8000/uploads/${article.images[0].filename}`" />
          </div>
          <div class="card-content">
            <span class="category">{{ article.category || 'GENERAL' }}</span>
            <h3>{{ article.title }}</h3>
            <p class="summary">{{ article.summary || article.content.substring(0, 100) }}...</p>
            <div class="meta">
              <span>{{ article.view_count }} 次閱讀</span>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- 文章列表 -->
    <section class="articles">
      <h2 class="section-title">[ POST_LOG ]</h2>
      <div class="article-grid">
        <article 
          v-for="article in articles" 
          :key="article.id"
          @click="viewArticle(article.id)"
          class="article-card"
        >
          <div class="image-wrapper">
            <div v-if="!article.images || !article.images[0]" class="placeholder-img">[ IMG ]</div>
            <img v-else :src="`http://localhost:8000/uploads/${article.images[0].filename}`" />
          </div>
          <div class="card-body">
            <span class="category-tag">{{ article.category || 'MISC' }}</span>
            <h3>{{ article.title }}</h3>
            <div class="tags">
              <span v-for="tag in article.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
            </div>
            <div class="meta">
              <span>👁 {{ article.view_count }}</span>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- 文章詳情 Modal -->
    <ArticleModal v-if="selectedArticle" :article="selectedArticle" @close="selectedArticle = null" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { articleAPI } from '../api'
import ArticleModal from './ArticleModal.vue'

export default {
  components: { ArticleModal },
  setup() {
    const articles = ref([])
    const featuredArticles = ref([])
    const searchQuery = ref('')
    const selectedArticle = ref(null)

    const loadArticles = async () => {
      const res = await articleAPI.getAll({ published_only: true })
      articles.value = res.data
    }

    const loadFeatured = async () => {
      const res = await articleAPI.getAll({ featured_only: true, limit: 3 })
      featuredArticles.value = res.data
    }

    const handleSearch = async () => {
      if (searchQuery.value.trim()) {
        const res = await articleAPI.search(searchQuery.value)
        articles.value = res.data
        featuredArticles.value = []
      } else {
        loadArticles()
        loadFeatured()
      }
    }

    const viewArticle = async (id) => {
      const res = await articleAPI.getOne(id)
      selectedArticle.value = res.data
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-TW', { year: 'numeric', month: 'short', day: 'numeric' })
    }

    onMounted(() => {
      loadArticles()
      loadFeatured()
    })

    return { articles, featuredArticles, searchQuery, selectedArticle, handleSearch, viewArticle, formatDate }
  }
}
</script>

<style scoped>
.search-section {
  margin-bottom: 40px;
}

.search-input {
  width: 100%;
  padding: 15px 20px;
  font-size: 16px;
  border: 3px solid #000;
  background: #fff;
  font-family: 'Courier New', monospace;
  box-shadow: 6px 6px 0 #000;
}

.search-input:focus {
  outline: none;
  background: #FFC107;
}

.section-title {
  font-family: 'Courier New', monospace;
  font-size: 24px;
  margin-bottom: 30px;
  letter-spacing: 3px;
  border-left: 6px solid #000;
  padding-left: 15px;
}

.featured {
  margin-bottom: 60px;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.featured-card {
  border: 4px solid #000;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 8px 8px 0 #000;
}

.featured-card:hover {
  transform: translate(-4px, -4px);
  box-shadow: 12px 12px 0 #000;
}

.image-wrapper {
  width: 100%;
  height: 250px;
  overflow: hidden;
  background: #000;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(100%);
  transition: all 1.5s ease;
}

.featured-card:hover .image-wrapper img,
.article-card:hover .image-wrapper img {
  filter: grayscale(0%) sepia(20%);
  transform: scale(1.05);
}

.placeholder-img {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  color: #FFC107;
  font-family: 'Courier New', monospace;
  font-size: 24px;
  font-weight: bold;
}

.card-content {
  padding: 25px;
}

.category {
  display: inline-block;
  background: #000;
  color: #FFC107;
  padding: 5px 12px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  margin-bottom: 15px;
}

.card-content h3 {
  font-size: 28px;
  margin-bottom: 15px;
  line-height: 1.3;
}

.summary {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 15px;
  color: #333;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: #666;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.article-card {
  border: 3px solid #000;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 5px 5px 0 #000;
}

.article-card:hover {
  transform: translate(-3px, -3px);
  box-shadow: 8px 8px 0 #000;
}

.article-card .image-wrapper {
  height: 180px;
}

.card-body {
  padding: 20px;
}

.category-tag {
  display: inline-block;
  background: #FFC107;
  color: #000;
  padding: 4px 10px;
  font-size: 10px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.card-body h3 {
  font-size: 20px;
  margin-bottom: 12px;
  line-height: 1.3;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.tag {
  font-size: 10px;
  padding: 3px 8px;
  border: 1px solid #000;
  font-family: 'Courier New', monospace;
}
</style>
