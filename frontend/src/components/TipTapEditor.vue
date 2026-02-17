<template>
  <div class="tiptap-editor">
    <!-- Toolbar -->
    <div class="toolbar">
      <button @click="editor?.chain().focus().toggleBold().run()" :class="{ active: editor?.isActive('bold') }" title="粗體">B</button>
      <button @click="editor?.chain().focus().toggleItalic().run()" :class="{ active: editor?.isActive('italic') }" title="斜體"><i>I</i></button>
      <span class="separator"></span>
      <button @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ active: editor?.isActive('heading', { level: 1 }) }">H1</button>
      <button @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ active: editor?.isActive('heading', { level: 2 }) }">H2</button>
      <button @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ active: editor?.isActive('heading', { level: 3 }) }">H3</button>
      <span class="separator"></span>
      <button @click="editor?.chain().focus().toggleBulletList().run()" :class="{ active: editor?.isActive('bulletList') }" title="無序列表">UL</button>
      <button @click="editor?.chain().focus().toggleOrderedList().run()" :class="{ active: editor?.isActive('orderedList') }" title="有序列表">OL</button>
      <button @click="editor?.chain().focus().toggleBlockquote().run()" :class="{ active: editor?.isActive('blockquote') }" title="引用">""</button>
      <button @click="editor?.chain().focus().toggleCodeBlock().run()" :class="{ active: editor?.isActive('codeBlock') }" title="程式碼區塊">&lt;/&gt;</button>
      <span class="separator"></span>
      <button @click="triggerUpload" title="上傳圖片">IMG</button>
      <button @click="openMediaLibrary" title="媒體庫">LIB</button>
      <button @click="editor?.chain().focus().setHorizontalRule().run()" title="分隔線">HR</button>
      <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" hidden />
    </div>

    <!-- Upload Indicator -->
    <div v-if="uploading" class="upload-indicator">上傳中...</div>

    <!-- Editor Content -->
    <editor-content :editor="editor" class="editor-content" />

    <!-- Media Library Modal -->
    <div v-if="showMediaLibrary" class="media-modal-overlay" @click.self="showMediaLibrary = false">
      <div class="media-modal">
        <h3>選擇圖片</h3>
        <div class="media-grid">
          <div v-for="img in mediaImages" :key="img.id" class="media-item" @click="selectMediaImage(img)">
            <img :src="getImageUrl(img.thumbnail_path || img.filepath)" :alt="img.alt_text || img.filename" />
          </div>
        </div>
        <div v-if="!mediaImages.length" class="empty-media">尚無圖片</div>
        <button @click="showMediaLibrary = false" class="close-media-btn">關閉</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Figure from '../extensions/figure'
import { mediaAPI } from '../api'

export default {
  components: { EditorContent },
  props: {
    modelValue: { type: String, default: '' }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const showMediaLibrary = ref(false)
    const mediaImages = ref([])
    const fileInput = ref(null)
    const uploading = ref(false)

    const getImageUrl = (path) => {
      if (!path) return ''
      const cleanPath = path.replace(/^uploads\//, '')
      return `/uploads/${cleanPath}`
    }

    const uploadAndInsert = async (file) => {
      if (!file || !file.type.startsWith('image/')) return
      uploading.value = true
      try {
        const res = await mediaAPI.upload(file)
        const img = res.data
        const url = getImageUrl(img.medium_path || img.filepath)
        editor.value?.chain().focus().insertFigure({ src: url, alt: img.alt_text || '' }).run()
      } catch (e) {
        console.error('Upload failed', e)
      }
      uploading.value = false
    }

    const editor = useEditor({
      content: props.modelValue,
      extensions: [
        StarterKit,
        Figure,
      ],
      onUpdate({ editor }) {
        emit('update:modelValue', editor.getHTML())
      },
      editorProps: {
        handleDrop(view, event) {
          const files = event.dataTransfer?.files
          if (files && files.length) {
            const imageFile = Array.from(files).find(f => f.type.startsWith('image/'))
            if (imageFile) {
              event.preventDefault()
              uploadAndInsert(imageFile)
              return true
            }
          }
          return false
        },
        handlePaste(view, event) {
          const items = event.clipboardData?.items
          if (items) {
            for (const item of items) {
              if (item.type.startsWith('image/')) {
                event.preventDefault()
                uploadAndInsert(item.getAsFile())
                return true
              }
            }
          }
          return false
        },
      },
    })

    watch(() => props.modelValue, (val) => {
      if (editor.value && editor.value.getHTML() !== val) {
        editor.value.commands.setContent(val, false)
      }
    })

    onBeforeUnmount(() => {
      editor.value?.destroy()
    })

    const triggerUpload = () => {
      fileInput.value?.click()
    }

    const handleFileUpload = (e) => {
      const file = e.target.files[0]
      if (file) uploadAndInsert(file)
      e.target.value = ''
    }

    const openMediaLibrary = async () => {
      try {
        const res = await mediaAPI.getAll()
        mediaImages.value = res.data
      } catch (e) {
        mediaImages.value = []
      }
      showMediaLibrary.value = true
    }

    const selectMediaImage = (img) => {
      const url = getImageUrl(img.medium_path || img.filepath)
      editor.value?.chain().focus().insertFigure({ src: url, alt: img.alt_text || '' }).run()
      showMediaLibrary.value = false
    }

    return {
      editor, showMediaLibrary, mediaImages, fileInput, uploading,
      triggerUpload, handleFileUpload, openMediaLibrary, selectMediaImage, getImageUrl
    }
  }
}
</script>

<style scoped>
.tiptap-editor {
  border: 3px solid #000;
  background: #fff;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  background: #000;
  border-bottom: 3px solid #000;
}

.toolbar button {
  padding: 6px 10px;
  background: #333;
  color: #FFC107;
  border: 1px solid #555;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  font-weight: bold;
  min-width: 32px;
  text-align: center;
}

.toolbar button:hover {
  background: #FFC107;
  color: #000;
}

.toolbar button.active {
  background: #FFC107;
  color: #000;
}

.separator {
  width: 1px;
  background: #555;
  margin: 0 4px;
}

.upload-indicator {
  background: #FFC107;
  color: #000;
  text-align: center;
  padding: 6px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: bold;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.editor-content {
  min-height: 300px;
  padding: 20px;
  font-family: Georgia, serif;
  font-size: 16px;
  line-height: 1.7;
}

.editor-content :deep(.tiptap) {
  outline: none;
  min-height: 300px;
}

.editor-content :deep(.tiptap h1) {
  font-size: 28px;
  font-weight: bold;
  margin: 20px 0 10px;
  border-bottom: 2px solid #000;
  padding-bottom: 5px;
}

.editor-content :deep(.tiptap h2) {
  font-size: 22px;
  font-weight: bold;
  margin: 18px 0 8px;
}

.editor-content :deep(.tiptap h3) {
  font-size: 18px;
  font-weight: bold;
  margin: 15px 0 6px;
}

.editor-content :deep(.tiptap blockquote) {
  border-left: 4px solid #FFC107;
  padding-left: 16px;
  margin: 15px 0;
  font-style: italic;
  color: #555;
}

.editor-content :deep(.tiptap pre) {
  background: #1a1a1a;
  color: #FFC107;
  padding: 16px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  overflow-x: auto;
  margin: 15px 0;
}

.editor-content :deep(.tiptap code) {
  background: #f5f5f5;
  padding: 2px 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.editor-content :deep(.tiptap figure) {
  width: 100%;
  margin: 20px 0;
  break-inside: avoid;
}

.editor-content :deep(.tiptap figure img) {
  max-width: 100%;
  height: auto;
  border: 2px solid #000;
  filter: grayscale(100%);
  box-shadow: 4px 4px 0 #000;
}

.editor-content :deep(.tiptap figure figcaption) {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-style: italic;
  text-align: center;
  color: #555;
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px solid #ccc;
}

.editor-content :deep(.tiptap ul),
.editor-content :deep(.tiptap ol) {
  padding-left: 24px;
  margin: 10px 0;
}

.editor-content :deep(.tiptap hr) {
  border: none;
  border-top: 2px solid #000;
  margin: 20px 0;
}

.editor-content :deep(.tiptap p) {
  margin-bottom: 12px;
}

/* Media Library Modal */
.media-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.media-modal {
  background: #FFFBEA;
  border: 4px solid #000;
  padding: 30px;
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.media-modal h3 {
  margin-bottom: 20px;
  font-family: 'Courier New', monospace;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.media-item {
  cursor: pointer;
  border: 2px solid #000;
  overflow: hidden;
  aspect-ratio: 1;
}

.media-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.media-item:hover img {
  transform: scale(1.1);
}

.empty-media {
  text-align: center;
  padding: 40px;
  color: #999;
  font-family: 'Courier New', monospace;
}

.close-media-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
  font-family: 'Courier New', monospace;
}
</style>
