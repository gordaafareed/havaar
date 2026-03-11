import { ref, watchEffect } from 'vue'
import { store } from '../store.js'
import { api } from '../services/api.js'
import { playUrl } from '../services/audio.js'
import RecordButton from './RecordButton.js'

export default {
  components: { RecordButton },
  setup() {
    const replyExists = ref(false)
    const previewUrl = ref(null)
    const previewOpen = ref(false)

    watchEffect(async () => {
      if (!store.activeSafeId) return
      const res = await fetch(
        api.outboundUrl(store.activeSafeId), { method: 'HEAD' }
      ).catch(() => ({ ok: false }))
      replyExists.value = res.ok
      previewOpen.value = false
    })

    function onSaved(blob) {
      replyExists.value = true
      previewUrl.value = URL.createObjectURL(blob)
      previewOpen.value = true
    }

    async function deleteReply() {
      if (!confirm('Delete this reply?')) return
      await api.deleteOutbound(store.activeSafeId)
      replyExists.value = false
      previewOpen.value = false
    }

    function playReply() {
      playUrl(api.outboundUrl(store.activeSafeId), null, null)
    }

    return { store, replyExists, previewUrl, previewOpen, onSaved, deleteReply, playReply }
  },
  template: `
    <div>
      <div class="section-label">
        your reply <span style="color:var(--dim)">(plays on next call)</span>
      </div>
      <div class="reply-box">

        <div class="reply-status">
          <span class="dot" :class="{ active: replyExists }"></span>
          {{ replyExists ? 'reply recorded — plays on next call' : 'no reply recorded' }}
        </div>

        <record-button
          target="reply"
          :safe-id="store.activeSafeId"
          @saved="onSaved"
        />

        <div style="display:flex;gap:8px;margin-top:12px;" v-if="replyExists">
          <button class="btn-action" @click="playReply">play</button>
          <button class="btn-action del" @click="deleteReply">delete</button>
        </div>

        <div class="preview-player" v-if="previewOpen && previewUrl">
          <div class="section-label">preview</div>
          <audio :src="previewUrl" controls
            style="width:100%;filter:invert(1) hue-rotate(180deg);"></audio>
        </div>

      </div>
    </div>
  `
}
