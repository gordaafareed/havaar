import { ref } from 'vue'
import { playUrl, stopPlayback } from '../services/audio.js'
import { relTime, randomBars } from '../services/format.js'
import { api } from '../services/api.js'

export default {
  props: {
    call: { type: Object, required: true },
  },
  setup(props) {
    const progress = ref(0)
    const playing = ref(false)
    const bars = randomBars()

    function toggle() {
      if (playing.value) {
        stopPlayback()
        playing.value = false
        progress.value = 0
      } else {
        playing.value = true
        playUrl(
          api.incomingUrl(props.call.filename),
          p => { progress.value = p * 100 },
          () => { playing.value = false; progress.value = 0 }
        )
      }
    }

    return { progress, playing, bars, toggle, relTime }
  },
  template: `
    <div class="audio-entry">
      <button class="play-btn" :class="{ playing }" @click="toggle">
        {{ playing ? '⏹' : '▶' }}
      </button>
      <div class="audio-info">
        <div class="audio-time">{{ relTime(call.timestamp) }}</div>
        <div class="audio-waveform">
          <div class="audio-progress" :style="{ width: progress + '%' }"></div>
          <div class="waveform-bars">
            <div
              v-for="(bar, i) in bars"
              :key="i"
              class="wbar"
              :style="{ height: bar.height + 'px' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  `
}
