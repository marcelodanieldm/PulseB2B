<template>
  <section>
    <h2 class="text-xl font-bold mb-4 tracking-tight text-indigo-400">Authentication</h2>
    <p class="mb-4 text-zinc-300">Authenticate using your API key. All requests must include the <span class="font-mono bg-zinc-800 px-2 py-1 rounded">Authorization</span> header.</p>
    <CodeBlock language="bash">
      curl -H "Authorization: Bearer &lt;api_key&gt;" https://api.pulseb2b.com/v1/resource
    </CodeBlock>
  </section>
</template>
<script>
import CodeBlock from '../CodeBlock.vue'
export default { name: 'AuthDocs', components: { CodeBlock } }
</script>
