<script setup>
import {ref} from 'vue'
import {useI18n} from 'vue-i18n'
import GradeInput from './GradeInput.vue'
import DateInput from './DateInput.vue'
import LoadError from './LoadError.vue'

defineProps({
  // [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}]
  categories: {type: Array, required: true},

  // subcategory id -> cell text exactly as shown: {3: '7,5', 4: ''}
  cellTexts: {type: Object, required: true},

  // subcategory id -> css state class: {3: 'grade-cell-new', 4: null}
  cellStates: {type: Object, required: true},

  // true while save is in flight, disables submit
  loading: Boolean,

  // true if any input is non-empty and invalid, disables submit
  hasGradeErrors: Boolean,

  // true if any input differs from the last saved value, disables submit when false
  hasChanges: Boolean,

  // true once the selected day's grades are loaded, the cells are hidden and submit disabled until then
  savedDayGradesReady: Boolean,

  // true when the selected day's grades failed to load
  // shows an inline message and a retry button instead of the cells, hides submit
  savedDayGradesFailed: Boolean,
})

// iso date string: '2024-01-31'
const inputGradeDate = defineModel('inputGradeDate', {type: String})

// edit: (subcategoryId, text) a box changed, the page owns cellTexts and writes it
// retry: the retry button was clicked after a failed load, the page reloads the same student and date
const emit = defineEmits(['submit', 'edit', 'retry'])

const {t} = useI18n()
const dateError = ref(false)
</script>

<template>
  <form
    class="form-card"
    @submit.prevent="emit('submit')"
  >
    <div class="grades-header">
      <span class="grades-title">{{ t('grades.add') }}</span>
    </div>

    <div class="date-field">
      <label>{{ t('grades.date') }}</label>
      <DateInput
        v-model="inputGradeDate"
        @error="dateError = $event"
      />
    </div>

    <div
      v-if="savedDayGradesReady && !dateError"
      class="cards-row"
    >
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="category-block"
      >
        <strong class="wrap-name">{{ cat.name }}</strong>
        <div class="cards-row">
          <div
            v-for="sub in cat.subcategories"
            :key="sub.id"
            class="subcategory-input-column"
          >
            <label class="wrap-name">{{ sub.name }}</label>
            <GradeInput
              :model-value="cellTexts[sub.id]"
              :state="cellStates[sub.id]"
              @update:model-value="emit('edit', sub.id, $event)"
            />
          </div>
        </div>
      </div>
    </div>
    <LoadError
      v-else-if="savedDayGradesFailed && !dateError"
      class="category-block"
      :message="t('grades.load_failed')"
      @retry="emit('retry')"
    />

    <button
      v-if="!savedDayGradesFailed"
      class="btn-primary"
      type="submit"
      :disabled="loading || !savedDayGradesReady || dateError || hasGradeErrors || !hasChanges"
    >
      {{ t('grades.save') }}
    </button>
  </form>
</template>
