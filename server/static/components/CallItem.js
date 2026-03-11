import { relTime } from '../services/format.js'
import { store } from '../store.js'

export default {
    props: {
        safeId: { type: String, required: true },
        calls: { type: Array, required: true },
    },
    emits: ['select'],
    setup(props, { emit }) {
        const label = () => store.contacts[props.safeId]?.label ?? ''
        const latest = () => props.calls[0]
        const unread = () => props.calls.some(c => !c.listened)
        const active = () => store.activeSafeId === props.safeId

        return { label, latest, unread, active, relTime, emit }
    },
    template: `
    <div
      class="call-item"
      :class="{ active: active(), unread: unread() }"
      @click="emit('select', safeId)"
    >
      <div class="call-number">{{ latest().caller }}</div>
      <div class="call-label" v-if="label()">{{ label() }}</div>
      <div class="call-time">
        {{ relTime(latest().timestamp) }} · {{ calls.length }} call{{ calls.length > 1 ? 's' : '' }}
      </div>
    </div>
  `
}