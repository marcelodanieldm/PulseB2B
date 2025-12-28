<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">Superuser Dashboard – Notificaciones</h1>
    <div class="mb-8">
      <h2 class="text-lg font-semibold mb-2 text-indigo-500">Nuevos usuarios Pro</h2>
      <ul>
        <li v-for="n in proNotifications" :key="n.id" class="mb-2 bg-zinc-900 rounded p-3 flex flex-col">
          <span class="font-medium">{{ n.name }} ({{ n.email }})</span>
          <span class="text-xs text-zinc-400">{{ n.time }} | {{ n.country }} | IP: {{ n.ip }}</span>
        </li>
      </ul>
    </div>
    <div>
      <h2 class="text-lg font-semibold mb-2 text-red-400">Desuscripciones</h2>
      <ul>
        <li v-for="n in unsubNotifications" :key="n.id" class="mb-2 bg-zinc-900 rounded p-3 flex flex-col">
          <span class="font-medium">{{ n.name }} ({{ n.email }})</span>
          <span class="text-xs text-zinc-400">{{ n.time }} | {{ n.country }} | IP: {{ n.ip }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'

const proNotifications = ref([])
const unsubNotifications = ref([])

async function fetchNotifications() {
  try {
    const res = await fetch('/api/admin/notifications?limit=50')
    const data = await res.json()
    proNotifications.value = data.filter(n => n.type === 'pro')
    unsubNotifications.value = data.filter(n => n.type === 'unsub')
  } catch (e) {
    // fallback: muestra vacío
    proNotifications.value = []
    unsubNotifications.value = []
  }
}

onMounted(() => {
  fetchNotifications()
  // Opcional: refresco cada 30s
  setInterval(fetchNotifications, 30000)
})
</script>
<style scoped>
</style>
