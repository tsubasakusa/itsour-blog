<template>
  <div class="admin-categories">
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { categoryAPI } from '../api'

export default {
  setup() {
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

    onMounted(() => {
      loadCategories()
    })

    return {
      categories, catForm, editingCatId,
      saveCategory, editCategory, deleteCategory, cancelCatForm,
    }
  }
}
</script>

<style scoped>
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
