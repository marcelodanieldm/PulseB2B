<template>
  <div class="relative flex flex-col items-center justify-center min-h-[60vh] bg-zinc-950 rounded-xl overflow-hidden border border-zinc-800 shadow-lg">
    <div class="absolute inset-0 backdrop-blur-sm opacity-80 z-0">
      <!-- Blurred docs preview (placeholder) -->
      <slot name="blurred-docs">
        <div class="h-full w-full flex items-center justify-center text-zinc-400 text-2xl font-semibold tracking-tight select-none">
          <span>Enterprise API Documentation</span>
        </div>
      </slot>
    </div>
    <div class="relative z-10 flex flex-col items-center justify-center py-16">
      <h2 class="text-3xl font-bold text-white mb-4 tracking-tight">Unlock Enterprise API Access</h2>
      <p class="text-zinc-400 mb-8 max-w-md text-center">Upgrade to the Enterprise plan to access advanced API documentation, live endpoint testing, and premium integrations.</p>
      <button class="px-8 py-3 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white font-semibold text-lg shadow-lg transition-all focus:outline-none focus:ring-2 focus:ring-indigo-400">
        Upgrade to Enterprise
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnterpriseTeaser',
}
</script>

<style scoped>
</style>
