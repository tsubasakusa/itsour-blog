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

    <!-- 頭條精選 -->
    <section v-if="!searchQuery && featuredArticles.length" class="featured">
      <div class="section-header">
        <span class="section-line"></span>
        <h2>FEATURED</h2>
        <span class="section-line"></span>
      </div>
      <div class="headline-layout">
        <!-- 頭條大圖 -->
        <article
          v-if="featuredArticles[0]"
          @click="viewArticle(featuredArticles[0])"
          class="headline-card"
        >
          <div class="image-wrapper headline-img">
            <div v-if="!getFirstImage(featuredArticles[0])" class="placeholder-img">HEADLINE</div>
            <img v-else :src="getFirstImage(featuredArticles[0])" :alt="featuredArticles[0].title" />
          </div>
          <div class="headline-content">
            <span class="category-badge">{{ getCategoryName(featuredArticles[0]) }}</span>
            <h2>{{ featuredArticles[0].title }}</h2>
            <p class="summary">{{ featuredArticles[0].summary || stripHtml(featuredArticles[0].content || '').substring(0, 150) }}...</p>
            <div class="meta-line">
              <span>{{ featuredArticles[0].author }}</span>
              <span>{{ formatDate(featuredArticles[0].created_at) }}</span>
              <span>{{ featuredArticles[0].reading_time || 1 }} 分鐘閱讀</span>
            </div>
          </div>
        </article>
        <!-- 側欄小文章 -->
        <div class="sidebar-articles" v-if="featuredArticles.length > 1">
          <article
            v-for="article in featuredArticles.slice(1)"
            :key="article.id"
            @click="viewArticle(article)"
            class="sidebar-card"
          >
            <div class="sidebar-img-wrapper" v-if="getFirstImage(article)">
              <img :src="getFirstImage(article)" :alt="article.title" />
            </div>
            <div class="sidebar-content">
              <span class="category-badge small">{{ getCategoryName(article) }}</span>
              <h4>{{ article.title }}</h4>
              <div class="meta-line small">
                <span>{{ formatDate(article.created_at) }}</span>
                <span>{{ article.reading_time || 1 }} 分鐘</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 分隔線 -->
    <div class="double-rule"></div>

    <!-- 文章列表 -->
    <section class="articles">
      <div class="section-header">
        <span class="section-line"></span>
        <h2>POST LOG</h2>
        <span class="section-line"></span>
      </div>
      <div class="article-grid">
        <article
          v-for="article in articles"
          :key="article.id"
          @click="viewArticle(article)"
          class="article-card"
        >
          <div class="image-wrapper">
            <div v-if="!getFirstImage(article)" class="placeholder-img">[ IMG ]</div>
            <img v-else :src="getFirstImage(article)" :alt="article.title" />
          </div>
          <div class="card-body">
            <span class="category-tag">{{ getCategoryName(article) }}</span>
            <h3>{{ article.title }}</h3>
            <div class="tags">
              <span v-for="tag in article.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
            </div>
            <div class="meta">
              <span>{{ article.reading_time || 1 }} 分鐘閱讀</span>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- 文章詳情 Modal -->
    <ArticleModal
      v-if="selectedArticle"
      :article="selectedArticle"
      @close="selectedArticle = null"
    />
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
      const res = await articleAPI.getAll({ featured_only: true, limit: 4 })
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

    const viewArticle = async (article) => {
      const res = article.slug
        ? await articleAPI.getBySlug(article.slug)
        : await articleAPI.getOne(article.id)
      selectedArticle.value = res.data
    }

    const getFirstImage = (article) => {
      if (article.images && article.images.length) {
        const img = article.images[0]
        const path = img.thumbnail_path || img.filepath
        if (path) return `/uploads/${path.replace(/^uploads\//, '')}`
      }
      if (article.cover_image) return article.cover_image
      return null
    }

    const getCategoryName = (article) => {
      if (article.category && article.category.name) return article.category.name
      return 'GENERAL'
    }

    const stripHtml = (html) => {
      return html.replace(/<[^>]+>/g, '')
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-TW', { year: 'numeric', month: 'short', day: 'numeric' })
    }

    onMounted(() => {
      loadArticles()
      loadFeatured()
    })

    return {
      articles, featuredArticles, searchQuery, selectedArticle,
      handleSearch, viewArticle, formatDate, getFirstImage, getCategoryName, stripHtml
    }
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

/* Section Headers */
.section-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.section-header h2 {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 4px;
  white-space: nowrap;
}

.section-line {
  flex: 1;
  height: 1px;
  background: #000;
}

/* Double Rule Divider */
.double-rule {
  border-top: 3px double #000;
  margin: 50px 0;
}

/* ===== Headline Layout ===== */
.headline-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.headline-card {
  border: 4px solid #000;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 8px 8px 0 #000;
}

.headline-card:hover {
  transform: translate(-4px, -4px);
  box-shadow: 12px 12px 0 #000;
}

.headline-img {
  height: 350px;
}

.headline-content {
  padding: 25px;
}

.headline-content h2 {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 32px;
  line-height: 1.2;
  margin-bottom: 12px;
}

.summary {
  font-size: 15px;
  line-height: 1.7;
  color: #333;
  margin-bottom: 12px;
  font-family: Georgia, serif;
}

/* Sidebar Articles */
.sidebar-articles {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  border: 3px solid #000;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 5px 5px 0 #000;
}

.sidebar-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 7px 7px 0 #000;
}

.sidebar-img-wrapper {
  height: 120px;
  overflow: hidden;
  background: #000;
}

.sidebar-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(100%);
  transition: filter 1.5s ease;
}

.sidebar-card:hover .sidebar-img-wrapper img {
  filter: grayscale(0%) sepia(20%);
}

.sidebar-content {
  padding: 15px;
}

.sidebar-content h4 {
  font-family: Georgia, serif;
  font-size: 16px;
  line-height: 1.3;
  margin-bottom: 8px;
}

/* Image Wrapper */
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

.headline-card:hover .image-wrapper img,
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

/* Category Badge */
.category-badge {
  display: inline-block;
  background: #000;
  color: #FFC107;
  padding: 5px 12px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  margin-bottom: 10px;
}

.category-badge.small {
  padding: 3px 8px;
  font-size: 10px;
}

/* Meta Line */
.meta-line {
  display: flex;
  gap: 15px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: #666;
}

.meta-line.small {
  font-size: 11px;
  gap: 10px;
}

/* ===== Article Grid ===== */
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
  font-family: Georgia, serif;
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

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: #666;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .headline-layout {
    grid-template-columns: 1fr;
  }

  .headline-img {
    height: 220px;
  }

  .headline-content h2 {
    font-size: 24px;
  }

  .article-grid {
    grid-template-columns: 1fr;
  }
}
</style>
