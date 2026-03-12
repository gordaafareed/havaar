import { store } from './store.js'
import { api } from './services/api.js'
import TopBar from './components/TopBar.js'
import Sidebar from './components/Sidebar.js'
import Main from './components/Main.js'

export default {
  components: { TopBar, Sidebar, 'main-view': Main },

  setup() {
    async function refresh() {
      try {
        const [status, data] = await Promise.all([
          api.getStatus(),
          api.getThreads(),
        ])
        store.status.live = status.ok
        store.status.defaultExists = status.default_exists
        store.threads = data.threads
        store.contacts = data.contacts
        store.status.broadcast_live = status.broadcast_live
        store.status.broadcast_draft = status.broadcast_draft
        store.status.broadcast_meta = status.broadcast_meta
      } catch {
        store.status.live = false
      }
    }

    refresh()
    setInterval(refresh, 8000)
    return { store }
  },

  template: `
    <div id="shell">
      <top-bar />
      <div class="layout">
        <sidebar />
        <main-view />
      </div>
    </div>
  `
}
