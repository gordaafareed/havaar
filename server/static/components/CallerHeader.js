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

    const incomingCount = () =>
      store.activeThread.filter(e => e.type === 'incoming').length

    const lastMessage = () =>
      [...store.activeThread].reverse().find(e => e.timestamp)

    return { store, saveLabel, relTime, incomingCount, lastMessage }
  },
  template: `
    <div class="main-header">
      <div class="caller-number">{{ store.activeCaller }}</div>
      <div class="caller-meta">
        <span>{{ incomingCount() }} message{{ incomingCount() > 1 ? 's' : '' }}</span>
        <span v-if="lastMessage()">last: {{ relTime(lastMessage().timestamp) }}</span>
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
