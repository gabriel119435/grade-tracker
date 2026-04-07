<script setup>
import {computed} from 'vue'
import {Line} from 'vue-chartjs'
import {CategoryScale, Chart as ChartJS, LinearScale, LineElement, PointElement, Tooltip} from 'chart.js'

// chart.js is tree-shakable: only the pieces you register are included in the bundle.
// CategoryScale x-axis with string labels
// LinearScale: y-axis with numeric values
// PointElement: the dots on the line
// LineElement: the line itself
// Tooltip: hover tooltip
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip)

const props = defineProps({
  grades: Array, // [{date: '2024-01-31', value: 7.5}] -- one entry per saved grade for this subcategory
})

// chart.js renders on a canvas, which is outside vue's templating system and cannot read css variables directly
// getComputedStyle reads the resolved value from the dom so chart.js can use the design token
const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--color-border-0').trim()

const data = computed(() => ({
  labels: props.grades.map(g => g.date), // date strings used as plain category labels
  datasets: [{
    data: props.grades.map(g => g.value),
    borderColor,
    borderWidth: 2,
    pointRadius: 1,
    clip: false    // allows point circles to render beyond y-axis min/max boundary (value 0 or 10)
  }]
}))

const options = computed(() => ({
  responsive: true,          // chart resizes with its container width
  maintainAspectRatio: true, // preserves aspectRatio below when container resizes
  aspectRatio: 2,            // width:height ratio, 2 means width is twice the height
  plugins: {
    tooltip: {displayColors: false} // removes colored square from tooltip; only one dataset, square adds nothing
  },
  scales: {
    x: {
      ticks: {
        maxRotation: 0,
        minRotation: 0,
        font: {size: 10},
        callback(value, index, ticks) {
          // show only first and last label; return null hides the label without removing the tick
          if (index === 0 || index === ticks.length - 1) return this.getLabelForValue(value)
          return null
        }
      }
    },
    y: {min: 0, max: 10} // grades are always in the 0–10 range
  },
}))
</script>

<template>
  <Line :data="data" :options="options"/>
</template>