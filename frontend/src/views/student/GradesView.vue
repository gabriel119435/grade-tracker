<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {store} from '../../store.js'
import {useLimit} from '../../composables/grades/useLimit.js'
import {useGradesLoader} from '../../composables/grades/useGradesLoader.js'
import GradeCharts from '../../components/GradeCharts.vue'
import GradeLimitControls from '../../components/GradeLimitControls.vue'

const grades = ref([])
const {loadGrades} = useGradesLoader()
const {limit, setLimit} = useLimit()

async function load() {
  const data = await loadGrades(store.user.id, limit.value)
  if (data) grades.value = data
}

watch(limit, load)
const hasGrades = computed(() =>
    grades.value.some(cat =>
        cat.subcategories.some(sub => sub.grades.length > 0)
    )
)

onMounted(load)
</script>

<template>
  <div class="vertical-stack">
    <GradeCharts :grades="grades">
      <template v-if="hasGrades" #controls>
        <GradeLimitControls :limit="limit" @set="setLimit"/>
      </template>
    </GradeCharts>
  </div>
</template>
