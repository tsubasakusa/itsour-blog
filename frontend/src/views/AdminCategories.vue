<template>
  <div class="admin-categories">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-text">LOADING...</p>
      </div>
    </div>

    <template v-else>
    <div class="cat-form">
      <input v-model="catForm.name" placeholder="分類名稱" />
      <input v-model="catForm.description" placeholder="描述（選填）" />
      <input v-model="catForm.color" type="color" />
      <button @click="saveCategory" class="save-btn">{{ editingCatId ? '更新' : '新增' }}</button>
      <button v-if="editingCatId" @click="cancelCatForm" class="cancel-btn">取消</button>
    </div>
    <div class="category-list">
      <div v-for="cat in categories" :key="cat.id" class="category-row">
        <span class="cat-color" :style="{ background: cat.color }"></span>
        <span class="cat-name">{{ cat.name }}</span>
        <span class="cat-slug">{{ cat.slug }}</span>
        <div class="cat-actions">
          <button @click="editCategory(cat)" class="edit-btn">編輯</button>
          <button @click="deleteCategory(cat.id)" class="delete-btn">刪除</button>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { categoryAPI } from '../api'

export default {
  setup() {
    const loading = ref(true)
    const categories = ref([])
    const editingCatId = ref(null)
    const catForm = ref({ name: '', description: '', color: '#FFC107' })

    const loadCategories = async () => {
      try {
        const res = await categoryAPI.getAll()
        categories.value = res.data
      } catch (e) { console.error(e) }
    }

    const saveCategory = async () => {
      if (editingCatId.value) {
        await categoryAPI.update(editingCatId.value, catForm.value)
      } else {
        await categoryAPI.create(catForm.value)
      }
      cancelCatForm()
      loadCategories()
    }

    const editCategory = (cat) => {
      editingCatId.value = cat.id
      catForm.value = { name: cat.name, description: cat.description || '', color: cat.color || '#FFC107' }
    }

    const deleteCategory = async (id) => {
      if (confirm('確定刪除此分類？')) {
        await categoryAPI.delete(id)
        loadCategories()
      }
    }

    const cancelCatForm = () => {
      editingCatId.value = null
      catForm.value = { name: '', description: '', color: '#FFC107' }
    }

    onMounted(async () => {
      try {
        await loadCategories()
      } finally {
        loading.value = false
      }
    })

    return {
      loading, categories, catForm, editingCatId,
      saveCategory, editCategory, deleteCategory, cancelCatForm,
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

.cat-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.cat-form input {
  padding: 10px;
  border: 2px solid #000;
  font-family: inherit;
}

.cat-form input[type="color"] {
  width: 50px;
  height: 40px;
  padding: 2px;
}

.category-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 2px solid #000;
  margin-bottom: 8px;
  background: #fff;
}

.cat-color {
  width: 20px;
  height: 20px;
  border: 1px solid #000;
}

.cat-name {
  font-weight: bold;
  font-family: 'Courier New', monospace;
}

.cat-slug {
  color: #999;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.cat-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.cat-actions button {
  padding: 5px 12px;
  font-size: 12px;
}

.save-btn {
  padding: 10px 20px;
  background: #000;
  color: #FFC107;
  border: none;
  cursor: pointer;
  font-family: 'Courier New', monospace;
}

.cancel-btn {
  padding: 10px 20px;
  background: #ccc;
  border: none;
  cursor: pointer;
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
