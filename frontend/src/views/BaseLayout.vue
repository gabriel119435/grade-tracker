<script setup>
import AppToast from '../components/AppToast.vue'
import AppTopBar from '../components/AppTopBar.vue'
</script>

<template>
  <div>
    <AppTopBar/>
    <RouterView/>
    <AppToast/>
  </div>
</template>
