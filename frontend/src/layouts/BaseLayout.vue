<script setup>
import AppToast from '../components/AppToast.vue'
import AppTopBar from '../components/AppTopBar.vue'
</script>

<template>
  <AppTopBar/>
  <RouterView/>
  <AppToast/>
</template>
