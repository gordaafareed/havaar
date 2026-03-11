import AudioEntry from './AudioEntry.js'
import { store } from '../store.js'

export default {
    components: { AudioEntry },
    setup() {
        return { store }
    },
    template: `
    <div>
      <div class="section-label">messages from caller</div>
      <audio-entry
        v-for="call in store.activeCalls"
        :key="call.id"
        :call="call"
      />
    </div>
  `
}
