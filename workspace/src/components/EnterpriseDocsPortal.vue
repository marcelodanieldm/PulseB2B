<template>
  <DocsLayout :activeSection="activeSection" @navigate="setSection">
    <div v-if="!isEnterprise">
      <EnterpriseTeaser>
        <template #blurred-docs>
          <div class="h-96 w-full flex items-center justify-center text-zinc-400 text-2xl font-semibold tracking-tight select-none opacity-60 blur-sm">
            <span>Enterprise API Documentation</span>
          </div>
        </template>
      </EnterpriseTeaser>
    </div>
    <div v-else>
      <!-- MDX/Docs content will be rendered here for enterprise users -->
      <component :is="currentSectionComponent" />
    </div>
  </DocsLayout>
</template>

<script>
import DocsLayout from './DocsLayout.vue'
import EnterpriseTeaser from './EnterpriseTeaser.vue'
// Import your docs sections as Vue components (to be replaced with MDX integration)
import AuthDocs from './docs/AuthDocs.vue'
import WebhooksDocs from './docs/WebhooksDocs.vue'
import HubSpotDocs from './docs/HubSpotDocs.vue'
import SlackDocs from './docs/SlackDocs.vue'

export default {
  name: 'EnterpriseDocsPortal',
  components: {
    DocsLayout,
    EnterpriseTeaser,
    AuthDocs,
    WebhooksDocs,
    HubSpotDocs,
    SlackDocs,
  },
  props: {
    planType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      activeSection: 'authentication',
    }
  },
  computed: {
    isEnterprise() {
      return this.planType === 'enterprise'
    },
    currentSectionComponent() {
      switch (this.activeSection) {
        case 'authentication': return 'AuthDocs'
        case 'webhooks': return 'WebhooksDocs'
        case 'hubspot': return 'HubSpotDocs'
        case 'slack': return 'SlackDocs'
        default: return 'AuthDocs'
      }
    },
  },
  methods: {
    setSection(section) {
      this.activeSection = section
    },
  },
}
</script>

<style scoped>
</style>
