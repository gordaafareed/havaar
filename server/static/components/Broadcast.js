import { ref } from 'vue'
import { store } from '../store.js'
import { api } from '../services/api.js'
import { playUrl } from '../services/audio.js'
import { relTime } from '../services/format.js'
import RecordButton from './RecordButton.js'

export default {
    components: { RecordButton },
    setup() {
        const title = ref('')
        const publishing = ref(false)

        async function onDraftSaved() {
            store.status.broadcast_draft = true
        }

        async function publish() {
            if (!title.value.trim()) {
                alert('Add a title so you know what this broadcast says')
                return
            }
            publishing.value = true
            await api.publishBroadcast(title.value.trim())
            const status = await api.getStatus()
            store.status.broadcast_live = status.broadcast_live
            store.status.broadcast_meta = status.broadcast_meta
            store.status.broadcast_draft = status.broadcast_draft
            title.value = ''
            publishing.value = false
        }

        async function unpublish() {
            if (!confirm('Take down the current broadcast?')) return
            await api.unpublishBroadcast()
            store.status.broadcast_live = false
            store.status.broadcast_meta = null
        }

        async function deleteDraft() {
            await api.deleteBroadcastDraft()
            store.status.broadcast_draft = false
        }

        function playLive() {
            playUrl(api.broadcastLiveUrl(), null, null)
        }

        function playDraft() {
            playUrl(api.broadcastDraftUrl(), null, null)
        }

        return {
            store, title, publishing, relTime,
            onDraftSaved, publish, unpublish,
            deleteDraft, playLive, playDraft
        }
    },
    template: `
    <div class="broadcast-panel">
      <div class="section-label">broadcast</div>

      <!-- live broadcast -->
      <div class="broadcast-live" v-if="store.status.broadcast_live">
        <div class="broadcast-status">
          <span class="dot active"></span>
          <span class="broadcast-title">{{ store.status.broadcast_meta?.title }}</span>
        </div>
        <div class="broadcast-meta-time" v-if="store.status.broadcast_meta?.published">
          published {{ relTime(store.status.broadcast_meta.published) }}
        </div>
        <div style="display:flex;gap:8px;margin-top:10px;">
          <button class="btn-action" @click="playLive">play</button>
          <button class="btn-action del" @click="unpublish">take down</button>
        </div>
      </div>

      <div class="broadcast-none" v-else>
        <span class="dot"></span> no live broadcast
      </div>

      <!-- draft -->
      <div class="broadcast-draft" style="margin-top:16px;">
        <div class="section-label">new broadcast</div>
        <record-button target="broadcast" @saved="onDraftSaved" />
        <div v-if="store.status.broadcast_draft" style="margin-top:10px;">
          <div style="display:flex;gap:8px;margin-bottom:10px;">
            <button class="btn-action" @click="playDraft">preview</button>
            <button class="btn-action del" @click="deleteDraft">discard</button>
          </div>
          <input
            class="label-input"
            v-model="title"
            placeholder="broadcast title / note…"
            style="width:100%;margin-bottom:8px;"
          />
          <button class="btn-action" @click="publish" :disabled="publishing">
            {{ publishing ? 'publishing…' : 'publish' }}
          </button>
        </div>
      </div>
    </div>
  `
}
