import { store } from '../store.js'
import CallItem from './CallItem.js'

export default {
  components: { CallItem },
  setup() {
    async function select(safeId) {
      store.activeSafeId = safeId
      const unlistened = (store.threads[safeId] ?? [])
        .filter(e => e.type === 'incoming' && !e.listened)
      for (const e of unlistened) {
        e.listened = true
        fetch(`/api/threads/${e.id}/listened`, {
          method: 'POST', credentials: 'include'
        })
      }
    }
    return { store, select }
  },
  template: `
    <div class="call-list">
      <div v-if="!store.callerList.length"
        style="padding:20px;font-size:11px;color:var(--dim);text-align:center;margin-top:20px;">
        no calls yet
      </div>
      <call-item
        v-for="item in store.callerList"
        :key="item.safeId"
        :item="item"
        @select="select"
      />
    </div>
  `
}
