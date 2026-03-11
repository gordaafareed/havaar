import { ref, watchEffect } from 'vue'
import { store } from '../store.js'
import { relTime } from '../services/format.js'
import ThreadMessage from './ThreadMessage.js'
import RecordBar from './RecordBar.js'
import CallerHeader from './CallerHeader.js'

export default {
    components: { ThreadMessage, RecordBar, CallerHeader },

    setup() {
        const thread = ref([])
        const threadEl = ref(null)

        watchEffect(() => {
            thread.value = store.activeThread ? [...store.activeThread] : []
            scrollToBottom()
        })

        function onDeleted(id) {
            thread.value = thread.value.filter(e => e.id !== id)
            const t = store.threads[store.activeSafeId]
            if (t) {
                const i = t.findIndex(e => e.id === id)
                if (i !== -1) t.splice(i, 1)
            }
        }

        function onSent({ res }) {
            thread.value.push({
                id: res.filename,
                type: 'outgoing',
                filename: res.filename,
                timestamp: new Date().toISOString(),
                pending: true,
                played: false,
            })
            scrollToBottom()
        }

        function scrollToBottom() {
            setTimeout(() => {
                if (threadEl.value)
                    threadEl.value.scrollTop = threadEl.value.scrollHeight
            }, 50)
        }

        return { store, thread, threadEl, onDeleted, onSent, relTime }
    },

    template: `
    <div style="flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;">
      <caller-header />
      <div class="thread-body" ref="threadEl">
        <div v-if="!thread.length" class="thread-empty">
          no messages yet
        </div>
        <thread-message
          v-for="entry in thread"
          :key="entry.id"
          :entry="entry"
          @deleted="onDeleted"
        />
      </div>
      <record-bar @sent="onSent" />
    </div>
  `
}
