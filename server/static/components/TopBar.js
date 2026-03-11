import { store } from '../store.js'
import { api } from '../services/api.js'

export default {
    setup() {
        async function logout() {
            await api.logout()
            window.location.href = '/login'
        }
        return { store, logout }
    },
    template: `
        <div class="topbar">
        <div class="topbar-left">
            <div class="logo">// havaar</div>
            <span class="status-dot" :class="{ live: store.status.live }"></span>
            <span class="status-text">{{ store.status.live ? 'live' : 'offline' }}</span>
        </div>
        <button class="btn-sm" @click="logout">logout</button>
        </div>
    `
}
