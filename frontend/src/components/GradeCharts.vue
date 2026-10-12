<script setup>
import {computed, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import GradeChart from './GradeChart.vue'
import GradeLimitControls from './GradeLimitControls.vue'
import LoadError from './LoadError.vue'
import {localizeGrade} from '../utils/gradeUtils.js'

const props = defineProps({
  // [{category: 'serve', subcategories: [{id: 3, name: 'slice', grades: [{id, date, value}]}]}]
  grades: {type: Array, required: true},

  // true when the chart load failed, shows an inline message and a retry button instead of the charts
  failed: Boolean,

  // true when grades belongs to the selected student and limit, nothing below the title shows until then
  ready: Boolean,
})

// grade history size picked with the limit buttons in the header: 5, 10 or 30, the parent reloads on change
const limit = defineModel('limit', {type: Number})

// retry: the retry button was clicked, the parent reloads the same student and limit
const emit = defineEmits(['retry'])

const {t} = useI18n()

// current locale decimal separator: ',' or '.'
const separator = computed(() => t('grade_input.decimal_separator'))

// set of collapsed category names: Set(['serve', 'forehand'])
const collapsedCategories = ref(new Set())

// per category: average of each subcategory's latest grade, one decimal in the locale format
// null without grades: {serve: '7,8'}
const categoryAverages = computed(() => {
  const result = {}
  for (const cat of props.grades) {
    const latestValues = cat.subcategories
      .map(sub => sub.grades.at(-1)?.value)
      .filter(v => v !== undefined)
    if (!latestValues.length) {
      result[cat.category] = null
      continue
    }
    const average = latestValues.reduce((a, b) => a + b, 0) / latestValues.length
    result[cat.category] = localizeGrade(average.toFixed(1), separator.value)
  }
  return result
})

function toggleCategory(name) {
  const collapsed = collapsedCategories.value
  if (collapsed.has(name)) collapsed.delete(name)
  else collapsed.add(name)
}
</script>

<template>
  <div class="history-card">
    <div class="grades-header">
      <span class="grades-title">{{ t('charts.title') }}</span>
      <GradeLimitControls v-model="limit"/>
    </div>

    <LoadError
      v-if="failed"
      class="category-card"
      :message="t('charts.load_failed')"
      @retry="emit('retry')"
    />
    <p v-else-if="ready && grades.length === 0">{{ t('charts.no_grades') }}</p>

    <div
      v-if="ready"
      class="categories-list"
    >
      <div
        v-for="category in grades"
        :key="category.category"
        class="category-card"
      >
        <h3>
          <button
            class="category-title"
            type="button"
            @click="toggleCategory(category.category)"
          >
            <span class="wrap-name">{{ category.category }}</span>
            <span
              v-if="categoryAverages[category.category] !== null"
              class="category-avg"
            >
              {{ t('charts.average') }}: {{ categoryAverages[category.category] }}
            </span>
          </button>
        </h3>
        <div
          v-if="!collapsedCategories.has(category.category)"
          class="cards-row"
        >
          <div
            v-for="subcat in category.subcategories"
            :key="subcat.id"
            class="chart-card"
          >
            <div class="subcat-badge">
              <span class="wrap-name">{{ subcat.name }}</span>
              <span
                v-if="subcat.grades.length"
                class="subcat-latest"
              >
                {{ t('charts.latest') }}: {{ localizeGrade(subcat.grades.at(-1).value, separator) }}
              </span>
            </div>
            <GradeChart :grades="subcat.grades"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
