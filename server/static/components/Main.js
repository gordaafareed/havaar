import EmptyState from './EmptyState.js'
import CallerDetail from './CallerDetail.js'
import { store } from '../store.js'

export default {
  components: { EmptyState, CallerDetail },
  setup() {
    return { store }
  },
  template: `
    <div class="main">
      <div v-if="!store.activeSafeId" class="main-body">
        <div class="empty-state">
          <div class="empty-icon">📞</div>
          <div class="empty-text">select a call</div>
        </div>
      </div>
      <caller-detail v-else />
    </div>
  `
}
