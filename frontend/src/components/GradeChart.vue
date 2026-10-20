<script setup>
import {computed} from 'vue'
import {Line} from 'vue-chartjs'
import {CategoryScale, Chart as ChartJS, LinearScale, LineElement, PointElement, Tooltip} from 'chart.js'
import {useI18n} from 'vue-i18n'
import {localizeDate} from '../utils/dateUtils.js'

// chart.js is tree-shakable: only the pieces registered here are included in the bundle
// CategoryScale: x-axis with string labels
// LinearScale: y-axis with numeric values
// PointElement: the dots on the line
// LineElement: the line itself
// Tooltip: hover tooltip
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip)

const props = defineProps({
  // one subcategory's last n grades, oldest first: [{id: 10, date: '2024-01-31', value: 7.5}]
  grades: {type: Array, required: true},
})

const {t, locale} = useI18n()

// chart.js renders on a canvas, which is outside vue's templating system and cannot read css variables directly
// getComputedStyle reads the resolved value from the dom so chart.js can use the design token
const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--color-b-2').trim()

const chartData = computed(() => ({
  // dates in the locale format used as plain category labels: '31/01/2024'
  labels: props.grades.map((g) => localizeDate(g.date, t('date_input.format'))),
  datasets: [
    {
      data: props.grades.map((g) => g.value),
      borderColor,
      borderWidth: 2,
      pointRadius: 1,
      // point circles render past the y-axis min/max (values 0 or 10)
      clip: false,
    },
  ],
}))

// computed: vue-chartjs only reapplies options when it gets a new object, a locale switch builds one
const chartOptions = computed(() => ({
  // tooltip value and y-axis numbers follow the app locale, not the browser's
  locale: locale.value,
  // resizes with the container width, keeping width twice the height
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    // no colored square in the tooltip, with one dataset it adds nothing
    tooltip: {displayColors: false},
  },
  scales: {
    x: {
      ticks: {
        maxRotation: 0,
        minRotation: 0,
        font: {size: 10},
        // shows only the first and last label, null hides a label but keeps its tick
        callback(value, index, ticks) {
          if (index === 0 || index === ticks.length - 1) return this.getLabelForValue(value)
          return null
        },
      },
    },
    // grades are always in the 0-10 range
    y: {min: 0, max: 10},
  },
}))
</script>

<template>
  <Line
    :data="chartData"
    :options="chartOptions"
  />
</template>
