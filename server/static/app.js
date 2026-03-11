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
                const [status, calls, contacts] = await Promise.all([
                    api.getStatus(),
                    api.getCalls(),
                    api.getContacts(),
                ])
                store.status.live = status.ok
                store.status.defaultExists = status.default_greeting
                store.calls = calls
                store.contacts = contacts
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
