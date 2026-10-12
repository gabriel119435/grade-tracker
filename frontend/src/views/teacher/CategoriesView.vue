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
import {useAction} from '../../composables/generic/useAction.js'
import {useConfirm} from '../../composables/generic/useConfirm.js'
import {useListLoad} from '../../composables/generic/useListLoad.js'
import {NAME_MAX_LENGTH} from '../../constants.js'
import LoadError from '../../components/LoadError.vue'

const {t} = useI18n()
// categories: [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}]
// full reload after every mutation; categories change infrequently so the extra request is imperceptible
const {items: categories, failed: categoriesFailed, load} = useListLoad(getCategories)
// new category input text: 'forehand'
const newCategoryName = ref('')
// categoryId -> new subcategory input text: {1: 'topspin'}
const newSubcategoryNames = ref({})

// no live checks on category and subcategory inputs: errors show only as toasts, so card height never changes

const {loading, withLoading} = useLoading()
const {runAction} = useAction(withLoading)
const {pendingId, confirm} = useConfirm()

onMounted(load)

async function handleCreateCategory() {
  await runAction(() => createCategory(newCategoryName.value), async () => {
    newCategoryName.value = ''
    await load()
  })
}

// 'cat-' and 'sub-' prefixes keep category and subcategory ids apart in the shared pendingId
async function handleDeleteCategory(id) {
  if (!confirm('cat-' + id)) return
  await runAction(() => deleteCategory(id), load)
}

async function handleCreateSubcategory(categoryId) {
  await runAction(() => createSubcategory(newSubcategoryNames.value[categoryId], categoryId), async () => {
    newSubcategoryNames.value[categoryId] = ''
    await load()
  })
}

async function handleDeleteSubcategory(id) {
  if (!confirm('sub-' + id)) return
  await runAction(() => deleteSubcategory(id), load)
}
</script>

<template>
  <div class="vertical-stack">
    <form
      class="single-line-form"
      @submit.prevent="handleCreateCategory"
    >
      <input
        v-model.trim="newCategoryName"
        required
        :placeholder="t('categories.new_category')"
        :maxlength="NAME_MAX_LENGTH"
      />
      <button
        class="btn-primary"
        type="submit"
        :disabled="loading"
      >
        {{ t('categories.add_category') }}
      </button>
    </form>

    <LoadError
      v-if="categoriesFailed"
      class="list-card"
      :message="t('categories.load_failed')"
      @retry="load"
    />
    <div
      v-else-if="categories.length"
      class="cards-row"
    >
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="list-card category-management"
      >
        <div class="category-header">
          <strong class="wrap-name">{{ cat.name }}</strong>
          <button
            :class="pendingId === 'cat-' + cat.id ? 'btn-danger-confirm' : 'btn-danger'"
            type="button"
            :disabled="loading"
            @click="handleDeleteCategory(cat.id)"
          >
            {{ pendingId === 'cat-' + cat.id ? t('common.confirmation') : t('common.delete') }}
          </button>
        </div>

        <div
          v-for="sub in cat.subcategories"
          :key="sub.id"
          class="item-row"
        >
          <span class="wrap-name">{{ sub.name }}</span>
          <button
            :class="pendingId === 'sub-' + sub.id ? 'btn-danger-confirm' : 'btn-danger'"
            type="button"
            :disabled="loading"
            @click="handleDeleteSubcategory(sub.id)"
          >
            {{ pendingId === 'sub-' + sub.id ? t('common.confirmation') : t('common.delete') }}
          </button>
        </div>

        <form @submit.prevent="handleCreateSubcategory(cat.id)">
          <input
            v-model.trim="newSubcategoryNames[cat.id]"
            required
            :placeholder="t('categories.new_subcategory')"
            :maxlength="NAME_MAX_LENGTH"
          />
          <button
            class="btn-primary"
            type="submit"
            :disabled="loading"
          >
            {{ t('categories.add_subcategory') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
