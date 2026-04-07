<script setup>
import {computed, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import GradeChart from './GradeChart.vue'

const {t} = useI18n()
const props = defineProps({
  grades: {type: Array, default: () => []},
})

// set of collapsed category names: Set(['Serve', 'Forehand'])
const collapsedCategories = ref(new Set())
const categoryAverages = computed(() => {
  const result = {}
  for (const cat of props.grades) {
    const latestValues = cat.subcategories
        .map(sub => sub.grades.at(-1)?.value) // grade with latest date
        .filter(v => v !== undefined)
    result[cat.category] = latestValues.length
        // calculate average
        ? (latestValues.reduce((a, b) => a + b, 0) / latestValues.length).toFixed(1)
        : null
  }
  return result
})

function toggleCategory(name) {
  const s = new Set(collapsedCategories.value)
  s.has(name) ? s.delete(name) : s.add(name)
  collapsedCategories.value = s
}
</script>

<template>
  <div class="history-card">
    <div class="grades-header">
      <span class="grades-title">{{ t('charts.title') }}</span>
      <slot name="controls"/>
    </div>

    <p v-if="grades.length === 0">{{ t('charts.no_grades') }}</p>

    <div class="categories-list">
      <div v-for="category in grades" :key="category.category" class="category-card">
        <h3 class="category-title" @click="toggleCategory(category.category)">
          <span>{{ category.category }}</span>
          <span v-if="categoryAverages[category.category] !== null" class="category-avg">
            {{ t('charts.average') }}: {{ categoryAverages[category.category] }}
          </span>
        </h3>
        <div v-if="!collapsedCategories.has(category.category)" class="cards-row">
          <div v-for="subcat in category.subcategories" :key="subcat.id" class="chart-card">
            <div class="subcat-badge">
              <span>{{ subcat.name }}</span>
              <span v-if="subcat.grades.length" class="subcat-latest">
                {{ t('charts.latest') }}: {{ subcat.grades.at(-1).value }}
              </span>
            </div>
            <GradeChart :grades="subcat.grades"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
