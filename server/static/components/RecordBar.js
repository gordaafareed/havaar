import { store } from '../store.js'
import { api } from '../services/api.js'
import { startRecording, stopRecording } from '../services/audio.js'

export default {
    emits: ['sent'],
    setup(_, { emit }) {
        let stream = null

        async function toggle() {
            if (store.recording.active) {
                const blob = await stopRecording(stream)
                stream = null
                store.recording.active = false
                store.recording.seconds = '0:00'
                const res = await api.uploadReply(store.activeSafeId, blob)
                emit('sent', { res, blob })
            } else {
                stream = await startRecording(tick => {
                    store.recording.seconds = tick
                })
                store.recording.active = true
            }
        }

        return { store, toggle }
    },
    template: `
    <div class="record-bar">
      <button
        class="btn-record"
        :class="{ recording: store.recording.active }"
        @click="toggle"
      >
        <span class="rec-dot"></span>
        {{ store.recording.active ? 'stop' : 'record reply' }}
      </button>
      <span class="rec-timer" v-if="store.recording.active">
        {{ store.recording.seconds }}
      </span>
      <span class="record-bar-hint" v-else>
        plays on caller's next call
      </span>
    </div>
  `
}
