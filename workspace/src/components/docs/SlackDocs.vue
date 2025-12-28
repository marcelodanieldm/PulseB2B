<template>
  <section>
    <h2 class="text-xl font-bold mb-4 tracking-tight text-indigo-400">Slack Integration</h2>
    <p class="mb-4 text-zinc-300">Integrate with Slack to receive notifications and automate workflows.</p>
    <CodeBlock language="js">
      // Example: Send Slack message
      fetch('https://api.pulseb2b.com/v1/slack/send', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer &lt;api_key&gt;',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel: '#general', text: 'Hello from PulseB2B!' })
      })
    </CodeBlock>
  </section>
</template>
<script>
import CodeBlock from '../CodeBlock.vue'
export default { name: 'SlackDocs', components: { CodeBlock } }
</script>
