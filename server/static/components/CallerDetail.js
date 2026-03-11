import CallerHeader from './CallerHeader.js'
import IncomingMessages from './IncomingMessages.js'
import ReplyBox from './ReplyBox.js'

export default {
    components: { CallerHeader, IncomingMessages, ReplyBox },
    template: `
    <div style="flex:1;display:flex;flex-direction:column;overflow:hidden;">
      <caller-header />
      <div class="main-body">
        <incoming-messages />
        <reply-box />
      </div>
    </div>
  `
}
