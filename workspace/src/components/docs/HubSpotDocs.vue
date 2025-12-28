<template>
  <section>
    <h2 class="text-xl font-bold mb-4 tracking-tight text-indigo-400">HubSpot Integration</h2>
    <p class="mb-4 text-zinc-300">Connect your HubSpot account to sync contacts and automate workflows.</p>
    <CodeBlock language="js">
      // Example: Sync contact
      fetch('https://api.pulseb2b.com/v1/hubspot/sync', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer &lt;api_key&gt;',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: 'user@example.com' })
      })
    </CodeBlock>
  </section>
</template>
<script>
import CodeBlock from '../CodeBlock.vue'
export default { name: 'HubSpotDocs', components: { CodeBlock } }
</script>
