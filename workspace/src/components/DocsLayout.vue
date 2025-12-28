<template>
  <div class="flex min-h-screen bg-zinc-950 text-white">
    <!-- Navigation -->
    <nav class="w-64 min-w-[16rem] border-r border-zinc-800 bg-zinc-950 py-10 px-6 flex flex-col gap-4">
      <h1 class="text-2xl font-bold mb-8 tracking-tight text-indigo-500">API Docs</h1>
      <ul class="flex flex-col gap-2">
        <li v-for="item in navItems" :key="item.label">
          <button
            class="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-900 transition-all font-medium"
            :class="{'bg-zinc-900 text-indigo-400': activeSection === item.section}"
            @click="$emit('navigate', item.section)"
          >
            {{ item.label }}
          </button>
        </li>
      </ul>
    </nav>
    <!-- Content -->
    <main class="flex-1 p-10 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>

<script>
export default {
  name: 'DocsLayout',
  props: {
    activeSection: {
      type: String,
      default: 'authentication',
    },
  },
  data() {
    return {
      navItems: [
        { label: 'Authentication', section: 'authentication' },
        { label: 'Webhooks', section: 'webhooks' },
        { label: 'HubSpot', section: 'hubspot' },
        { label: 'Slack', section: 'slack' },
      ],
    }
  },
}
</script>

<style scoped>
</style>
