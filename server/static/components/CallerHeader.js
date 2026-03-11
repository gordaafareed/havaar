import { store } from '../store.js'
import { api } from '../services/api.js'
import { relTime } from '../services/format.js'

export default {
    setup() {
        async function saveLabel(e) {
            const label = e.target.value.trim()
            await api.setLabel(store.activeSafeId, label)
            store.contacts[store.activeSafeId].label = label
        }

        return { store, saveLabel, relTime }
    },
    template: `
    <div class="main-header">
      <div class="caller-number">{{ store.activeCaller }}</div>
      <div class="caller-meta">
        <span>{{ store.activeCalls.length }} call{{ store.activeCalls.length > 1 ? 's' : '' }}</span>
        <span>last: {{ relTime(store.activeCalls[0].timestamp) }}</span>
      </div>
      <input
        class="label-input"
        :value="store.activeLabel"
        placeholder="add a name or label…"
        @blur="saveLabel"
        @keydown.enter="$event.target.blur()"
      />
    </div>
  `
}
