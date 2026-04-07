<script setup>
import {useToast} from '../composables/generic/useToast.js'

// useToast holds module-level singleton references.
// every AppToast instance (one per layout) reads the same message/type, so they all render identically.
// intentional: only one is ever mounted at a time per route, but the shared state means they don't need coordination.
const {message, type} = useToast()
</script>

<template>
  <Transition name="toast">
    <div v-if="message" :class="`app-toast--${type}`" class="app-toast">{{ message }}</div>
  </Transition>
</template>
