<script setup>
import {onMounted, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {
  createCategory,
  createSubcategory,
  deleteCategory,
  deleteSubcategory,
  getCategories
} from '../../api/routes/categories.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useToast} from '../../composables/generic/useToast.js'
import {useConfirm} from '../../composables/generic/useConfirm.js'
import {translateError} from '../../utils/translateError.js'

const categories = ref([]) // [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}]
const newCategoryName = ref('') // bound to the new category input: 'forehand'
const newSubcategoryNames = ref({}) // categoryId:new subcategory input: {1: 'topspin'}
const {t} = useI18n()
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {pendingId, confirm} = useConfirm()

async function load() {
  // full reload after every mutation; categories change infrequently so the extra request is imperceptible
  const data = await getCategories()
  if (!data.error) categories.value = data
}

onMounted(load)

async function handleCreateCategory() {
  await withLoading(async () => {
    const data = await createCategory(newCategoryName.value)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      newCategoryName.value = ''
      await load()
    }
  })
}

async function handleDeleteCategory(id) {
  if (!confirm('cat-' + id)) return // 'cat-' prefix avoids id collision with subcategories in the shared pendingId ref
  await withLoading(async () => {
    const data = await deleteCategory(id)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      await load()
    }
  })
}

async function handleCreateSubcategory(categoryId) {
  await withLoading(async () => {
    const data = await createSubcategory(newSubcategoryNames.value[categoryId], categoryId)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      newSubcategoryNames.value[categoryId] = ''
      await load()
    }
  })
}

async function handleDeleteSubcategory(id) {
  if (!confirm('sub-' + id)) return // 'sub-' prefix avoids id collision with categories in the shared pendingId ref
  await withLoading(async () => {
    const data = await deleteSubcategory(id)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      await load()
    }
  })
}
</script>

<template>
  <div class="vertical-stack">
    <form class="single-line-form" @submit.prevent="handleCreateCategory">
      <input v-model.trim="newCategoryName" :placeholder="t('categories.new_category')" maxlength="25" required/>
      <button :disabled="loading" class="btn-primary" type="submit">{{ t('categories.add_category') }}</button>
    </form>

    <div class="cards-row">
      <div v-for="cat in categories" :key="cat.id" class="list-card category-management">
        <div class="category-header">
          <strong>{{ cat.name }}</strong>
          <button :disabled="loading" :class="pendingId === 'cat-' + cat.id ? 'btn-danger-confirm' : 'btn-danger'"
                  @click="handleDeleteCategory(cat.id)">
            {{ pendingId === 'cat-' + cat.id ? t('common.confirmation') : t('common.delete') }}
          </button>
        </div>

        <div v-for="sub in cat.subcategories" :key="sub.id" class="item-row">
          <span>{{ sub.name }}</span>
          <button :disabled="loading" :class="pendingId === 'sub-' + sub.id ? 'btn-danger-confirm' : 'btn-danger'"
                  @click="handleDeleteSubcategory(sub.id)">
            {{ pendingId === 'sub-' + sub.id ? t('common.confirmation') : t('common.delete') }}
          </button>
        </div>

        <form @submit.prevent="handleCreateSubcategory(cat.id)">
          <input v-model.trim="newSubcategoryNames[cat.id]" :placeholder="t('categories.new_subcategory')"
                 maxlength="25" required/>
          <button :disabled="loading" class="btn-primary" type="submit">{{ t('categories.add_subcategory') }}</button>
        </form>
      </div>
    </div>
  </div>
</template>
