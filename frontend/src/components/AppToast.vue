<script setup>
import {useToast} from '../composables/generic/useToast.js'

// one AppToast per layout (BaseLayout, TabLayout), only one layout is mounted at a time
const {message, type} = useToast()
</script>

<template>
  <Transition name="toast">
    <div
      v-if="message"
      class="app-toast"
      :class="`app-toast--${type}`"
    >
      {{ message }}
    </div>
  </Transition>
</template>
