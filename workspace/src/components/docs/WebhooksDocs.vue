<template>
  <section>
    <h2 class="text-xl font-bold mb-4 tracking-tight text-indigo-400">Webhooks</h2>
    <p class="mb-4 text-zinc-300">Configure your webhook endpoint to receive real-time notifications.</p>
    <CodeBlock language="json">
      {
        "event": "user.created",
        "data": {
          "id": "123",
          "email": "user@example.com"
        }
      }
    </CodeBlock>
    <button class="mt-2 bg-zinc-700 hover:bg-zinc-800 text-white px-3 py-1 rounded shadow flex items-center gap-1" @click="$emit('test-endpoint')">
      <span>Play</span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-6.518-3.759A1 1 0 007 8.06v7.882a1 1 0 001.234.97l6.518-1.868A1 1 0 0016 14.06V9.94a1 1 0 00-1.248-.772z" /></svg>
    </button>
  </section>
</template>
<script>
import CodeBlock from '../CodeBlock.vue'
export default { name: 'WebhooksDocs', components: { CodeBlock } }
</script>
