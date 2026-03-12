import { reactive } from 'vue'

export const store = reactive({
    threads: {},
    contacts: {},
    activeSafeId: null,

    status: {
        live: false,
        defaultExists: false,
    },

    recording: {
        active: false,
        seconds: '0:00',
    },

    broadcast: {
        live: false,
        draft: false,
        meta: null,
    },

    get activeThread() {
        if (!this.activeSafeId) return []
        return this.threads[this.activeSafeId] ?? []
    },

    get activeCaller() {
        const t = this.activeThread
        const entry = t.find(e => e.caller)
        return entry?.caller ?? this.activeSafeId
    },

    get activeLabel() {
        return this.contacts[this.activeSafeId]?.label ?? ''
    },

    get unreadCount() {
        let count = 0
        for (const thread of Object.values(this.threads)) {
            count += thread.filter(e => e.type === 'incoming' && !e.listened).length
        }
        return count
    },

    get callerList() {
        return Object.entries(this.threads).map(([safeId, thread]) => {
            const latest = [...thread].reverse().find(e => e.timestamp)
            const unread = thread.some(e => e.type === 'incoming' && !e.listened)
            const caller = thread.find(e => e.caller)?.caller ?? safeId
            const label = this.contacts[safeId]?.label ?? ''
            return { safeId, caller, label, latest, unread }
        }).sort((a, b) =>
            new Date(b.latest?.timestamp ?? 0) - new Date(a.latest?.timestamp ?? 0)
        )
    },
})
