<script setup>
import {ref} from 'vue'
import {useI18n} from 'vue-i18n'
import GradeInput from './GradeInput.vue'
import DateInput from './DateInput.vue'

const {t} = useI18n()
const dateError = ref(null)

defineProps({
  categories: Array,            // [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}]
  inputGradeDate: String,       // iso date string: '2024-01-31'
  inputGradeEdits: Object,      // subcategory id -> cell text exactly as shown: {3: '7,5', 4: ''}
  cellStates: Object,           // subcategory id -> css state class: {3: 'grade-cell-new', 4: null}
  loading: Boolean,             // true while save is in flight; disables submit
  hasGradeErrors: Boolean,      // true if any input is non-empty and invalid; disables submit
  hasChanges: Boolean,          // true if any input differs from last saved value; disables submit when false
})

// edit: (subcategoryId, text) a box changed; the page owns inputGradeEdits and writes it
const emit = defineEmits(['update:inputGradeDate', 'submit', 'edit'])
</script>

<template>
  <form class="form-card" @submit.prevent="emit('submit')">
    <div class="grades-header">
      <span class="grades-title">{{ t('grades.add') }}</span>
    </div>

    <div class="date-field">
      <label>{{ t('grades.date') }}</label>
      <DateInput
          :modelValue="inputGradeDate"
          @update:modelValue="emit('update:inputGradeDate', $event)"
          @error="dateError = $event"
      />
    </div>

    <div class="cards-row">
      <div v-for="cat in categories" :key="cat.id" class="category-block">
        <strong>{{ cat.name }}</strong>
        <div class="cards-row">
          <div v-for="sub in cat.subcategories" :key="sub.id" class="subcategory-input-column">
            <label>{{ sub.name }}</label>
            <GradeInput
                :modelValue="inputGradeEdits[sub.id]"
                @update:modelValue="emit('edit', sub.id, $event)"
                :state="cellStates[sub.id]"
            />
          </div>
        </div>
      </div>
    </div>

    <button :disabled="loading || dateError || hasGradeErrors || !hasChanges" class="btn-primary" type="submit">
      {{ t('grades.save') }}
    </button>
  </form>
</template>
