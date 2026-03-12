export const api = {
    async getStatus() { return _get('/api/status') },
    async getThreads() { return _get('/api/threads') },
    async getThread(safeId) { return _get(`/api/threads/${safeId}`) },

    async markListened(entryId) { return _post(`/api/threads/${entryId}/listened`) },
    async deleteIncoming(entryId) { return _delete(`/api/threads/${entryId}`) },
    async setLabel(safeId, label) { return _post(`/api/contacts/${safeId}/label`, { label }) },

    async uploadReply(safeId, blob) { return _uploadAudio(`/api/reply/${safeId}`, blob) },
    async uploadDefault(blob) { return _uploadAudio('/api/outbound/default', blob) },
    async deleteDefault() { return _delete('/api/outbound/default') },

    async logout() { return _post('/logout') },

    async deleteOutgoing(entryId) { return _delete(`/api/reply/${entryId}`) },

    async uploadBroadcastDraft(blob) { return _uploadAudio('/api/broadcast/draft', blob) },
    async publishBroadcast(title) { return _post('/api/broadcast/publish', { title }) },
    async unpublishBroadcast() { return _post('/api/broadcast/unpublish') },
    async deleteBroadcastDraft() { return _delete('/api/broadcast/draft') },

    broadcastLiveUrl: () => `/api/audio/outbound/broadcast_live.wav`,
    broadcastDraftUrl: () => `/api/audio/outbound/broadcast_draft.wav`,

    incomingUrl: (filename) => `/api/audio/incoming/${filename}`,
    outgoingUrl: (filename) => `/api/audio/outgoing/${filename}`,
    defaultUrl: () => `/api/audio/outbound/default.wav`,
}

async function _get(url) {
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) throw new Error(`GET ${url} → ${res.status}`)
    return res.json()
}

async function _post(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: body ? { 'Content-Type': 'application/json' } : {},
        body: body ? JSON.stringify(body) : undefined,
    })
    if (!res.ok) throw new Error(`POST ${url} → ${res.status}`)
    return res.json()
}

async function _delete(url) {
    const res = await fetch(url, { method: 'DELETE', credentials: 'include' })
    if (!res.ok) throw new Error(`DELETE ${url} → ${res.status}`)
    return res.json()
}

async function _uploadAudio(url, blob) {
    const form = new FormData()
    form.append('audio', blob, 'recording.webm')
    const res = await fetch(url, { method: 'POST', credentials: 'include', body: form })
    if (!res.ok) throw new Error(`UPLOAD ${url} → ${res.status}`)
    return res.json()
}

