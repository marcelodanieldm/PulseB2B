<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">Visualización de Usuarios</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
      <div class="bg-zinc-900 rounded p-6 flex flex-col items-center">
        <span class="text-4xl font-bold text-indigo-400">{{ freeCount }}</span>
        <span class="text-zinc-300 mt-2">Usuarios Free</span>
      </div>
      <div class="bg-zinc-900 rounded p-6 flex flex-col items-center">
        <span class="text-4xl font-bold text-green-400">{{ proCount }}</span>
        <span class="text-zinc-300 mt-2">Usuarios Pro</span>
      </div>
      <div class="bg-zinc-900 rounded p-6 flex flex-col items-center">
        <span class="text-4xl font-bold text-yellow-400">{{ enterpriseCount }}</span>
        <span class="text-zinc-300 mt-2">Usuarios Enterprise</span>
      </div>
    </div>
    <div class="mb-8">
      <h2 class="text-lg font-semibold mb-2 text-indigo-500">Usuarios por Servicio Contratado</h2>
      <ul>
        <li v-for="(count, service) in usersByService" :key="service" class="mb-2 flex justify-between bg-zinc-800 rounded p-3">
          <span class="font-medium">{{ service }}</span>
          <span class="text-indigo-300">{{ count }}</span>
        </li>
      </ul>
    </div>
    <div>
      <h2 class="text-lg font-semibold mb-2 text-indigo-500">Origen de Usuarios (País)</h2>
      <ul>
        <li v-for="(count, country) in usersByCountry" :key="country" class="mb-2 flex justify-between bg-zinc-800 rounded p-3">
          <span class="font-medium">{{ country }}</span>
          <span class="text-indigo-300">{{ count }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'

const freeCount = ref(0)
const proCount = ref(0)
const enterpriseCount = ref(0)
const usersByService = ref({})
const usersByCountry = ref({})

async function fetchStats() {
  try {
    const res = await fetch('/api/admin/user-stats')
    const data = await res.json()
    freeCount.value = data.freeCount
    proCount.value = data.proCount
    enterpriseCount.value = data.enterpriseCount
    usersByService.value = data.usersByService
    usersByCountry.value = data.usersByCountry
  } catch (e) {
    freeCount.value = 0
    proCount.value = 0
    enterpriseCount.value = 0
    usersByService.value = {}
    usersByCountry.value = {}
  }
}

onMounted(fetchStats)
</script>
<style scoped>
</style>
