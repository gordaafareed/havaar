const { reactive } = Vue

export const store = reactive({
    calls: [],
    contacts: {},
    activeSafeId: null,
    status: {
        live: false,
        defaultExists: false,
    },
    recording: {
        active: false,
        target: null,     // 'reply' | 'default'
        seconds: '0:00',
    },
    playback: {
        filename: null,
        progress: 0,
    },

    get activeCalls() {
        if (!this.activeSafeId) return []
        return this.calls.filter(c => c.safe_id === this.activeSafeId)
    },

    get activeCaller() {
        return this.activeCalls[0]?.caller ?? null
    },

    get activeLabel() {
        return this.contacts[this.activeSafeId]?.label ?? ''
    },

    get unreadCount() {
        return this.calls.filter(c => !c.listened).length
    },

    get groupedCalls() {
        const groups = {}
        for (const c of this.calls) {
            if (!groups[c.safe_id]) groups[c.safe_id] = []
            groups[c.safe_id].push(c)
        }
        return groups
    },
})
