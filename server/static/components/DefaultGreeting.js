import { store } from '../store.js'
import { api } from '../services/api.js'
import { playUrl } from '../services/audio.js'
import RecordButton from './RecordButton.js'

export default {
  components: { RecordButton },
  setup() {
    function onSaved() {
      store.status.defaultExists = true
    }

    async function deleteDefault() {
      if (!confirm('Delete default greeting?')) return
      await api.deleteDefault()
      store.status.defaultExists = false
    }

    function playDefault() {
      playUrl(api.defaultUrl(), null, null)
    }

    return { store, onSaved, deleteDefault, playDefault }
  },
  template: `
    <div class="default-panel">
      <div class="section-label">default greeting</div>
      <div class="reply-status">
        <span class="dot" :class="{ active: store.status.defaultExists }"></span>
        {{ store.status.defaultExists ? 'recorded' : 'not recorded' }}
      </div>
      <record-button target="default" @saved="onSaved" />
      <div style="display:flex;gap:8px;margin-top:12px;" v-if="store.status.defaultExists">
        <button class="btn-action" @click="playDefault">play</button>
        <button class="btn-action del" @click="deleteDefault">delete</button>
      </div>
    </div>
  `
}
