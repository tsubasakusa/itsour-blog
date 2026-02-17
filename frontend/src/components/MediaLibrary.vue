<template>
  <div class="media-library">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-text">LOADING...</p>
      </div>
    </div>

    <template v-else>
    <h3 class="section-title">[ MEDIA_LIBRARY ]</h3>

    <!-- Upload Area -->
    <div class="upload-area"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="handleDrop"
      :class="{ 'drag-over': dragOver }"
    >
      <input type="file" ref="fileInput" @change="handleFileSelect" multiple accept="image/*" hidden />
      <p>拖曳圖片到此處或 <button @click="$refs.fileInput.click()" class="upload-btn">選擇檔案</button></p>
    </div>

    <p v-if="uploadStatus" class="upload-status">{{ uploadStatus }}</p>

    <!-- Select / Delete Actions -->
    <div v-if="selectedIds.size > 0" class="bulk-actions">
      <span>已選 {{ selectedIds.size }} 張</span>
      <button @click="deleteSelected" class="delete-btn">刪除選取</button>
      <button @click="selectedIds.clear()" class="cancel-btn">取消選取</button>
    </div>

    <!-- Media Grid -->
    <div class="media-grid">
      <div
        v-for="img in images"
        :key="img.id"
        class="media-card"
        :class="{ selected: selectedIds.has(img.id) }"
        @click="toggleSelect(img.id)"
      >
        <img :src="getImageUrl(img.thumbnail_path || img.filepath)" :alt="img.alt_text || img.filename" />
        <div class="media-info">
          <span class="filename">{{ img.filename }}</span>
          <span class="size" v-if="img.width">{{ img.width }}x{{ img.height }}</span>
        </div>
        <button class="copy-btn" @click.stop="copyUrl(img)" title="複製 URL">URL</button>
      </div>
    </div>

    <p v-if="!images.length" class="empty">尚無圖片</p>
    </template>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { mediaAPI } from '../api'

export default {
  setup() {
    const loading = ref(true)
    const images = ref([])
    const dragOver = ref(false)
    const uploadStatus = ref('')
    const selectedIds = reactive(new Set())

    const getImageUrl = (path) => {
      if (!path) return ''
      const cleanPath = path.replace(/^uploads\//, '')
      return `/uploads/${cleanPath}`
    }

    const loadImages = async () => {
      try {
        const res = await mediaAPI.getAll()
        images.value = res.data
      } catch (e) {
        console.error('Failed to load media', e)
      }
    }

    const uploadFiles = async (files) => {
      uploadStatus.value = `上傳中... (0/${files.length})`
      for (let i = 0; i < files.length; i++) {
        await mediaAPI.upload(files[i])
        uploadStatus.value = `上傳中... (${i + 1}/${files.length})`
      }
      uploadStatus.value = `上傳完成 (${files.length} 張)`
      setTimeout(() => uploadStatus.value = '', 3000)
      loadImages()
    }

    const handleFileSelect = (e) => {
      const files = Array.from(e.target.files)
      if (files.length) uploadFiles(files)
    }

    const handleDrop = (e) => {
      dragOver.value = false
      const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
      if (files.length) uploadFiles(files)
    }

    const toggleSelect = (id) => {
      if (selectedIds.has(id)) selectedIds.delete(id)
      else selectedIds.add(id)
    }

    const deleteSelected = async () => {
      if (!confirm(`確定刪除 ${selectedIds.size} 張圖片？`)) return
      for (const id of selectedIds) {
        await mediaAPI.delete(id)
      }
      selectedIds.clear()
      loadImages()
    }

    const copyUrl = (img) => {
      const url = window.location.origin + getImageUrl(img.medium_path || img.filepath)
      navigator.clipboard.writeText(url)
      uploadStatus.value = '已複製 URL'
      setTimeout(() => uploadStatus.value = '', 2000)
    }

    onMounted(async () => {
      try {
        await loadImages()
      } finally {
        loading.value = false
      }
    })

    return { loading, images, dragOver, uploadStatus, selectedIds, getImageUrl, handleFileSelect, handleDrop, toggleSelect, deleteSelected, copyUrl, loadImages }
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

.section-title {
  font-family: 'Courier New', monospace;
  font-size: 22px;
  margin-bottom: 20px;
  letter-spacing: 3px;
  border-left: 6px solid #000;
  padding-left: 15px;
}

.upload-area {
  border: 3px dashed #000;
  padding: 30px;
  text-align: center;
  margin-bottom: 20px;
  background: #fff;
  transition: all 0.3s;
  font-family: 'Courier New', monospace;
}

.upload-area.drag-over {
  background: #FFC107;
  border-style: solid;
}

.upload-btn {
  padding: 6px 16px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
  font-family: 'Courier New', monospace;
}

.upload-status {
  font-family: 'Courier New', monospace;
  color: #00aa00;
  margin-bottom: 15px;
}

.bulk-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
  font-family: 'Courier New', monospace;
}

.delete-btn {
  padding: 6px 14px;
  background: #f44336;
  color: #fff;
  border: none;
  cursor: pointer;
}

.cancel-btn {
  padding: 6px 14px;
  background: #ccc;
  border: none;
  cursor: pointer;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 15px;
}

.media-card {
  border: 2px solid #000;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: #fff;
  transition: all 0.2s;
}

.media-card.selected {
  border-color: #FFC107;
  box-shadow: 0 0 0 3px #FFC107;
}

.media-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.media-info {
  padding: 8px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
}

.filename {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.size {
  color: #999;
}

.copy-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  padding: 3px 8px;
  background: #000;
  color: #FFC107;
  border: none;
  font-size: 10px;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  opacity: 0;
  transition: opacity 0.2s;
}

.media-card:hover .copy-btn {
  opacity: 1;
}

.empty {
  text-align: center;
  padding: 40px;
  color: #999;
  font-family: 'Courier New', monospace;
}
</style>
