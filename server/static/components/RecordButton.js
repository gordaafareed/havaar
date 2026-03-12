import { store } from '../store.js'
import { startRecording, stopRecording } from '../services/audio.js'
import { api } from '../services/api.js'

export default {
    props: {
        target: { type: String, required: true },  // 'reply' | 'default'
        safeId: { type: String, default: null },
    },
    emits: ['saved'],
    setup(props, { emit }) {
        let stream = null

        const isMe = () =>
            store.recording.active && store.recording.target === props.target

        async function toggle() {
            if (isMe()) {
                const blob = await stopRecording(stream)
                stream = null
                store.recording.active = false
                store.recording.target = null
                store.recording.seconds = '0:00'
                if (props.target === 'default') {
                    await api.uploadDefault(blob)
                    store.status.defaultExists = true
                } else if (props.target === 'broadcast') {
                    await api.uploadBroadcastDraft(blob)
                } else {
                    await api.uploadOutbound(props.safeId, blob)
                }
                emit('saved', blob)
            } else {
                stream = await startRecording(tick => {
                    store.recording.seconds = tick
                })
                store.recording.active = true
                store.recording.target = props.target
            }
        }

        return { store, isMe, toggle }
    },
    template: `
    <div class="record-controls">
      <button
        class="btn-record"
        :class="{ recording: isMe() }"
        @click="toggle"
      >
        <span class="rec-dot"></span>
        {{ isMe() ? 'stop' : (target === 'reply' ? 'record reply' : 'record') }}
      </button>
      <span class="rec-timer" v-if="isMe()">{{ store.recording.seconds }}</span>
    </div>
  `
}
