<script setup>
import {onMounted, ref, watch} from 'vue'
import {store} from '../../store.js'
import {useChartGrades} from '../../composables/grades/useChartGrades.js'
import {GRADE_HISTORY_LIMITS} from '../../constants.js'
import GradeCharts from '../../components/GradeCharts.vue'

const {chartGrades, chartGradesReady, chartGradesFailed, loadChartGrades} = useChartGrades()
const limit = ref(GRADE_HISTORY_LIMITS[0])

// the logged-in student's own charts
const load = () => loadChartGrades(store.user.id, limit.value)

onMounted(load)
watch(limit, load)
</script>

<template>
  <div class="vertical-stack">
    <GradeCharts
      v-model:limit="limit"
      :grades="chartGrades"
      :ready="chartGradesReady"
      :failed="chartGradesFailed"
      @retry="load"
    />
  </div>
</template>
