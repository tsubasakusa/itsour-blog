<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">✕</button>
      
      <!-- 文章頭部 -->
      <header class="article-header">
        <span class="category">{{ article.category || 'GENERAL' }}</span>
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span>作者：{{ article.author }}</span>
          <span>{{ formatDate(article.created_at) }}</span>
          <span>閱讀：{{ article.view_count }} 次</span>
        </div>
        <div class="tags">
          <span v-for="tag in article.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
        </div>
      </header>

      <!-- 文章內容 -->
      <article class="article-body">
        <p class="drop-cap-paragraph" v-html="formatContent(article.content)"></p>
        
        <!-- 圖片展示 -->
        <div v-if="article.images && article.images.length" class="images-section">
          <figure v-for="img in article.images" :key="img.id" class="article-image">
            <img :src="`http://localhost:8000/uploads/${img.filename}`" :alt="img.alt_text || article.title" />
            <figcaption v-if="img.alt_text">{{ img.alt_text }}</figcaption>
          </figure>
        </div>
      </article>
    </div>
  </div>
</template>

<script>
export default {
  props: ['article'],
  emits: ['close'],
  setup() {
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-TW', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
      })
    }

    const formatContent = (content) => {
      const firstChar = content.charAt(0)
      const rest = content.slice(1)
      return `<span class="drop-cap">${firstChar}</span>${rest}`
    }

    return { formatDate, formatContent }
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
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.modal-content {
  background: #FFFBEA;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border: 6px solid #000;
  box-shadow: 0 0 60px rgba(0, 0, 0, 0.5);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #000;
  color: #FFC107;
  border: none;
  width: 40px;
  height: 40px;
  font-size: 24px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #FFC107;
  color: #000;
  transform: rotate(90deg);
}

.article-header {
  padding: 60px 60px 40px;
  border-bottom: 3px double #000;
  background: #FFC107;
}

.article-header .category {
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
  font-size: 48px;
  line-height: 1.2;
  margin-bottom: 20px;
  text-shadow: 3px 3px 0 rgba(0, 0, 0, 0.1);
}

.article-meta {
  display: flex;
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

.article-body {
  padding: 60px;
  font-size: 18px;
  line-height: 1.8;
  column-count: 2;
  column-gap: 40px;
  column-rule: 1px solid #ddd;
}

.drop-cap-paragraph :deep(.drop-cap) {
  float: left;
  font-size: 72px;
  line-height: 60px;
  padding: 8px 12px 0 0;
  font-weight: bold;
  font-family: Georgia, serif;
}

.article-body p {
  margin-bottom: 20px;
  text-align: justify;
}

.images-section {
  column-span: all;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 2px solid #000;
}

.article-image {
  margin-bottom: 30px;
  break-inside: avoid;
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
  transform: scale(1.02);
}

.article-image figcaption {
  margin-top: 10px;
  font-size: 13px;
  font-style: italic;
  text-align: center;
  font-family: 'Courier New', monospace;
  color: #666;
}

@media (max-width: 768px) {
  .article-body {
    column-count: 1;
    padding: 30px;
  }
  
  .article-header {
    padding: 40px 30px 30px;
  }
  
  .article-title {
    font-size: 32px;
  }
}
</style>
