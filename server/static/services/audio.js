import { fmtSecs } from './format.js'

// ── playback ───────────────────────────────────────────────────────────────────
let _audio = null
let _progCb = null
let _progInterval = null

export function playUrl(url, onProgress, onEnd) {
    stopPlayback()
    _audio = new Audio(url + '?t=' + Date.now())
    _progCb = onProgress
    _audio.play()
    _progInterval = setInterval(() => {
        if (_audio && _audio.duration && _progCb)
            _progCb(_audio.currentTime / _audio.duration)
    }, 200)
    _audio.onended = () => { stopPlayback(); onEnd?.() }
}

export function stopPlayback() {
    if (_audio) { _audio.pause(); _audio.currentTime = 0 }
    if (_progInterval) clearInterval(_progInterval)
    _audio = _progCb = _progInterval = null
}

// ── recording ──────────────────────────────────────────────────────────────────
let _recorder = null
let _chunks = []
let _timer = null
let _onTick = null
let _seconds = 0

export async function startRecording(onTick) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    _chunks = []
    _seconds = 0
    _onTick = onTick
    _recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    _recorder.ondataavailable = e => _chunks.push(e.data)
    _recorder.start()
    _timer = setInterval(() => { _seconds++; _onTick?.(fmtSecs(_seconds)) }, 1000)
    return stream
}

export function stopRecording(stream) {
    return new Promise(resolve => {
        _recorder.onstop = () => {
            clearInterval(_timer)
            stream.getTracks().forEach(t => t.stop())
            resolve(new Blob(_chunks, { type: 'audio/webm' }))
        }
        _recorder.stop()
    })
}
