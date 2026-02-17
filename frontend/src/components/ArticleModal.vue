<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">&#10005;</button>

      <!-- Cover Image -->
      <div v-if="coverImage" class="cover-image">
        <img :src="coverImage" :alt="article.title" />
      </div>

      <!-- 文章頭部 -->
      <header class="article-header">
        <span class="category-badge">{{ categoryName }}</span>
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span>{{ article.author }}</span>
          <span>{{ formatDate(article.created_at) }}</span>
          <span v-if="categoryName !== 'GENERAL'">{{ categoryName }}</span>
          <span>{{ article.reading_time || 1 }} 分鐘閱讀</span>
          <span>{{ article.view_count }} 次瀏覽</span>
        </div>
        <div class="tags" v-if="article.tags && article.tags.length">
          <span v-for="tag in article.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
        </div>
      </header>

      <!-- 文章內容 -->
      <article class="article-body" v-html="formattedContent"></article>

      <!-- 圖片展示 -->
      <div v-if="extraImages.length" class="images-section">
        <figure v-for="img in extraImages" :key="img.id" class="article-image">
          <img :src="getImageUrl(img.medium_path || img.filepath)" :alt="img.alt_text || article.title" />
          <figcaption v-if="img.alt_text">{{ img.alt_text }}</figcaption>
        </figure>
      </div>

      <!-- 相關文章 -->
      <section v-if="relatedArticles.length" class="related-section">
        <div class="related-header">
          <span class="related-line"></span>
          <h3>RELATED POSTS</h3>
          <span class="related-line"></span>
        </div>
        <div class="related-grid">
          <article
            v-for="rel in relatedArticles"
            :key="rel.id"
            class="related-card"
            @click="$emit('close'); viewRelated(rel)"
          >
            <div class="related-img" v-if="getFirstImage(rel)">
              <img :src="getFirstImage(rel)" :alt="rel.title" />
            </div>
            <div class="related-body">
              <span class="related-category">{{ getRelCategoryName(rel) }}</span>
              <h4>{{ rel.title }}</h4>
              <span class="related-time">{{ rel.reading_time || 1 }} 分鐘閱讀</span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { articleAPI } from '../api'

export default {
  props: ['article'],
  emits: ['close'],
  setup(props) {
    const relatedArticles = ref([])

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    }

    const getImageUrl = (path) => {
      if (!path) return ''
      return `/uploads/${path.replace(/^uploads\//, '')}`
    }

    const categoryName = computed(() => {
      if (props.article.category && props.article.category.name) return props.article.category.name
      return 'GENERAL'
    })

    const coverImage = computed(() => {
      if (!props.article.images || !props.article.images.length) return null
      const img = props.article.images[0]
      return getImageUrl(img.medium_path || img.filepath)
    })

    const extraImages = computed(() => {
      if (!props.article.images) return []
      return props.article.images.slice(1)
    })

    const formattedContent = computed(() => {
      let content = props.article.content || ''
      // Add drop-cap to first paragraph if it's a <p> tag
      content = content.replace(/^(<p>)([^<])/, '$1<span class="drop-cap">$2</span>')
      return content
    })

    const getFirstImage = (article) => {
      if (!article.images || !article.images.length) return null
      const img = article.images[0]
      return getImageUrl(img.thumbnail_path || img.filepath)
    }

    const getRelCategoryName = (article) => {
      if (article.category && article.category.name) return article.category.name
      return 'GENERAL'
    }

    const viewRelated = async (rel) => {
      // This would need parent handling; for now just close
    }

    const loadRelated = async () => {
      try {
        const res = await articleAPI.getRelated(props.article.id)
        relatedArticles.value = res.data
      } catch (e) {
        relatedArticles.value = []
      }
    }

    onMounted(loadRelated)

    return {
      relatedArticles, formatDate, getImageUrl, categoryName,
      coverImage, extraImages, formattedContent, getFirstImage, getRelCategoryName, viewRelated
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.modal-content {
  background: #FFFBEA;
  max-width: 900px;
  width: 100%;
  border: 6px solid #000;
  box-shadow: 0 0 60px rgba(0, 0, 0, 0.5);
  position: relative;
  margin: 40px 0;
}

.close-btn {
  position: fixed;
  top: 30px;
  right: 30px;
  background: #000;
  color: #FFC107;
  border: none;
  width: 40px;
  height: 40px;
  font-size: 20px;
  cursor: pointer;
  z-index: 1010;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #FFC107;
  color: #000;
  transform: rotate(90deg);
}

/* Cover Image */
.cover-image {
  width: 100%;
  max-height: 450px;
  overflow: hidden;
}

.cover-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(100%);
  transition: filter 2s ease;
}

.cover-image:hover img {
  filter: grayscale(0%) sepia(15%);
}

/* Header */
.article-header {
  padding: 50px 60px 40px;
  border-bottom: 3px double #000;
  background: #FFC107;
}

.category-badge {
  display: inline-block;
  background: #000;
  color: #FFC107;
  padding: 6px 15px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  margin-bottom: 20px;
}

.article-title {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 48px;
  font-weight: 900;
  line-height: 1.15;
  margin-bottom: 20px;
  text-shadow: 3px 3px 0 rgba(0, 0, 0, 0.08);
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  margin-bottom: 15px;
  color: #333;
}

.tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  padding: 5px 12px;
  border: 2px solid #000;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  background: #fff;
}

/* Article Body - Rich Text Styles */
.article-body {
  padding: 60px;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 18px;
  line-height: 1.8;
  column-count: 2;
  column-gap: 40px;
  column-rule: 1px solid #ddd;
}

.article-body :deep(.drop-cap) {
  float: left;
  font-size: 72px;
  line-height: 60px;
  padding: 8px 12px 0 0;
  font-weight: bold;
  font-family: Georgia, serif;
}

.article-body :deep(p) {
  margin-bottom: 18px;
  text-align: justify;
}

.article-body :deep(h1) {
  column-span: all;
  font-size: 32px;
  font-weight: 900;
  margin: 30px 0 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #000;
  font-family: Georgia, serif;
}

.article-body :deep(h2) {
  column-span: all;
  font-size: 26px;
  font-weight: bold;
  margin: 25px 0 12px;
  font-family: Georgia, serif;
}

.article-body :deep(h3) {
  font-size: 20px;
  font-weight: bold;
  margin: 20px 0 10px;
  font-family: Georgia, serif;
}

.article-body :deep(blockquote) {
  column-span: all;
  border-left: 5px solid #FFC107;
  padding: 15px 25px;
  margin: 20px 0;
  font-style: italic;
  font-size: 20px;
  color: #444;
  background: rgba(255, 193, 7, 0.05);
}

.article-body :deep(pre) {
  column-span: all;
  background: #1a1a1a;
  color: #FFC107;
  padding: 20px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  overflow-x: auto;
  margin: 20px 0;
  border-left: 4px solid #FFC107;
}

.article-body :deep(code) {
  background: #f5f0e0;
  padding: 2px 6px;
  font-family: 'Courier New', monospace;
  font-size: 15px;
}

.article-body :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

.article-body :deep(figure) {
  column-span: all;
  width: 100%;
  margin: 25px 0;
  break-inside: avoid;
}

.article-body :deep(figure img) {
  max-width: 100%;
  height: auto;
  border: 3px solid #000;
  filter: grayscale(100%);
  transition: filter 2s ease;
  box-shadow: 6px 6px 0 #000;
}

.article-body :deep(figure:hover img) {
  filter: grayscale(0%) sepia(15%);
}

.article-body :deep(figure figcaption) {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-style: italic;
  text-align: center;
  color: #666;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #999;
}

.article-body :deep(img) {
  column-span: all;
  max-width: 100%;
  height: auto;
  border: 3px solid #000;
  margin: 20px 0;
  filter: grayscale(100%);
  transition: filter 2s ease;
}

.article-body :deep(img:hover) {
  filter: grayscale(0%) sepia(15%);
}

.article-body :deep(ul),
.article-body :deep(ol) {
  padding-left: 25px;
  margin: 15px 0;
}

.article-body :deep(li) {
  margin-bottom: 6px;
}

.article-body :deep(hr) {
  column-span: all;
  border: none;
  border-top: 2px solid #000;
  margin: 30px 0;
}

.article-body :deep(a) {
  color: #000;
  border-bottom: 2px solid #FFC107;
  text-decoration: none;
  transition: background 0.3s;
}

.article-body :deep(a:hover) {
  background: #FFC107;
}

/* Images Section */
.images-section {
  padding: 40px 60px;
  border-top: 2px solid #000;
}

.article-image {
  margin-bottom: 30px;
}

.article-image img {
  width: 100%;
  height: auto;
  border: 4px solid #000;
  filter: grayscale(100%);
  transition: all 2s ease;
  box-shadow: 6px 6px 0 #000;
}

.article-image:hover img {
  filter: grayscale(0%) sepia(15%);
  transform: scale(1.01);
}

.article-image figcaption {
  margin-top: 10px;
  font-size: 13px;
  font-style: italic;
  text-align: center;
  font-family: 'Courier New', monospace;
  color: #666;
}

/* Related Articles Section */
.related-section {
  padding: 40px 60px;
  border-top: 3px double #000;
  background: #f9f5e3;
}

.related-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.related-header h3 {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  letter-spacing: 3px;
  white-space: nowrap;
}

.related-line {
  flex: 1;
  height: 1px;
  background: #000;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.related-card {
  border: 2px solid #000;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.related-card:hover {
  transform: translateY(-3px);
  box-shadow: 4px 4px 0 #000;
}

.related-img {
  height: 120px;
  overflow: hidden;
  background: #000;
}

.related-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(100%);
  transition: filter 1s;
}

.related-card:hover .related-img img {
  filter: grayscale(0%) sepia(20%);
}

.related-body {
  padding: 12px;
}

.related-category {
  font-size: 10px;
  font-family: 'Courier New', monospace;
  color: #666;
  letter-spacing: 1px;
}

.related-body h4 {
  font-family: Georgia, serif;
  font-size: 14px;
  line-height: 1.3;
  margin: 5px 0;
}

.related-time {
  font-size: 11px;
  font-family: 'Courier New', monospace;
  color: #999;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .article-body {
    column-count: 1;
    padding: 30px;
  }

  .article-header {
    padding: 40px 30px 30px;
  }

  .article-title {
    font-size: 28px;
  }

  .related-grid {
    grid-template-columns: 1fr;
  }

  .images-section,
  .related-section {
    padding: 30px;
  }
}
</style>
