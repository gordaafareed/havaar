import { ref } from 'vue'
import { store } from '../store.js'
import { api } from '../services/api.js'
import { playUrl, stopPlayback } from '../services/audio.js'
import { relTime } from '../services/format.js'

export default {
  props: {
    entry: { type: Object, required: true },
  },
  emits: ['deleted'],
  setup(props, { emit }) {
    const progress = ref(0)
    const playing = ref(false)

    const isIncoming = () => props.entry.type === 'incoming'
    const hasAudio = () => !!props.entry.filename
    const isGhost = () => props.entry.type === 'outgoing' && !props.entry.filename

    async function togglePlay() {
      if (playing.value) {
        stopPlayback()
        playing.value = false
        progress.value = 0
        return
      }
      const url = isIncoming()
        ? api.incomingUrl(props.entry.filename)
        : api.outgoingUrl(props.entry.filename)

      playing.value = true
      await playUrl(
        url,
        p => { progress.value = p * 100 },
        () => { playing.value = false; progress.value = 0 }
      )
    }

    async function deleteEntry() {
      if (isIncoming()) {
        if (!confirm('Delete this message?')) return
        await api.deleteIncoming(props.entry.id)
        emit('deleted', props.entry.id)
      } else {
        if (!confirm('Delete this reply? The caller will not hear it.')) return
        await api.deleteOutgoing(props.entry.id)
        emit('deleted', props.entry.id)
      }
    }

    return { isIncoming, hasAudio, isGhost, playing, progress, togglePlay, deleteEntry, relTime }
  },
  template: `
    <div class="thread-msg" :class="isIncoming() ? 'msg-in' : 'msg-out'">

      <!-- ghost outgoing -->
      <div v-if="isGhost()" class="msg-ghost">
        voice message · sent · {{ relTime(entry.timestamp) }}
      </div>

      <!-- audio message -->
      <div v-else class="msg-bubble">
        <div class="msg-waveform">
          <button class="play-btn" :class="{ playing }" @click="togglePlay">
            {{ playing ? '⏹' : '▶' }}
          </button>
          <div class="audio-waveform" style="flex:1;">
            <div class="audio-progress" :style="{ width: progress + '%' }"></div>
            <div class="waveform-bars">
              <div v-for="n in 36" :key="n" class="wbar"
                :style="{ height: (4 + Math.random() * 18) + 'px' }"></div>
            </div>
          </div>
        </div>
        <div class="msg-meta">
            <span>{{ relTime(entry.timestamp) }}</span>
            <button
                v-if="isIncoming() || (entry.type === 'outgoing' && entry.pending)"
                class="msg-delete"
                @click="deleteEntry"
            >delete</button>
        </div>
      </div>

      <!-- panic alert -->
      <div v-if="entry.type === 'panic'" class="msg-panic">
        🚨 panic alert · {{ relTime(entry.timestamp) }}
      </div>

    </div>
  `
}
