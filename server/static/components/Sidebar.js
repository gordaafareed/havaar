import Broadcast from './Broadcast.js'
import CallList from './CallList.js'
import DefaultGreeting from './DefaultGreeting.js'
import { store } from '../store.js'

export default {
  components: { CallList, DefaultGreeting, Broadcast },
  setup() {
    return { store }
  },
  template: `
    <div class="sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">calls</span>
        <span class="badge" v-if="store.unreadCount">{{ store.unreadCount }}</span>
      </div>
      <call-list />
      <broadcast />
    </div>
  `
}
