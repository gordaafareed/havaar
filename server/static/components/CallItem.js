import { store } from '../store.js'
import { relTime } from '../services/format.js'

export default {
  props: {
    item: { type: Object, required: true },
  },
  emits: ['select'],
  setup(props, { emit }) {
    const active = () => store.activeSafeId === props.item.safeId
    return { active, relTime, emit }
  },
  template: `
    <div
      class="call-item"
      :class="{ active: active(), unread: item.unread }"
      @click="emit('select', item.safeId)"
    >
      <div class="call-number">{{ item.caller }}</div>
      <div class="call-label" v-if="item.label">{{ item.label }}</div>
      <div class="call-time" v-if="item.latest">
        {{ relTime(item.latest.timestamp) }}
      </div>
    </div>
  `
}
