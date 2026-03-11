import { store } from '../store.js'
import { api } from '../services/api.js'
import CallItem from './CallItem.js'

export default {
    components: { CallItem },
    setup() {
        async function select(safeId) {
            store.activeSafeId = safeId
            const unlistened = store.calls.filter(c => c.safe_id === safeId && !c.listened)
            await Promise.all(unlistened.map(c => api.markListened(c.id)))
            unlistened.forEach(c => { c.listened = true })
        }

        return { store, select }
    },
    template: `
    <div class="call-list">
      <div v-if="!Object.keys(store.groupedCalls).length"
        style="padding:20px;font-size:11px;color:var(--dim);text-align:center;margin-top:20px;">
        no calls yet
      </div>
      <call-item
        v-for="(calls, safeId) in store.groupedCalls"
        :key="safeId"
        :safe-id="safeId"
        :calls="calls"
        @select="select"
      />
    </div>
  `
}
