<script setup>
import {createStudent, deleteStudent, getStudents} from '../../api/routes/students.js'
import UserList from '../../components/UserList.vue'

// api functions handed to UserList
const studentApi = {get: getStudents, create: createStudent, remove: deleteStudent}
</script>

<template>
  <div class="vertical-stack">
    <UserList
      :api="studentApi"
      i18n-prefix="students"
    />
  </div>
</template>
