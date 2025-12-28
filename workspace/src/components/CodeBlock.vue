<template>
  <pre class="rounded-lg bg-zinc-900 p-4 overflow-x-auto text-sm relative">
    <code :class="`language-${language}`" ref="codeBlock"><slot /></code>
    <button class="absolute right-6 top-6 bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded shadow" @click="copyCode">Copy</button>
  </pre>
</template>

<script>
import Prism from 'prismjs'
import 'prismjs/themes/prism-solarizedlight.css'

export default {
  name: 'CodeBlock',
  props: {
    language: {
      type: String,
      default: 'js',
    },
  },
  mounted() {
    this.highlight()
  },
  updated() {
    this.highlight()
  },
  methods: {
    highlight() {
      if (this.$refs.codeBlock) {
        Prism.highlightElement(this.$refs.codeBlock)
      }
    },
    copyCode() {
      const code = this.$refs.codeBlock.textContent
      navigator.clipboard.writeText(code)
    },
  },
}
</script>

<style scoped>
pre {
  background: #0f172a;
  color: #e5e7eb;
}
button {
  font-size: 0.9rem;
}
</style>
