<script>
import { nextTick } from 'vue'
import http from '../utils/http.js'
import { Histogram, SwitchButton, RefreshRight,
  Promotion, Opportunity } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  data() {
    return {
      openid: '',
      sessionId: '',
      isPhone: false,

      msgList: [],
      msg: '',          // 当前用户输入框中的消息
      chatContext: [],  // 当前保持的聊天上下文

      botList: [],      // 机器人信息列表
      rankList: [],     // 排行榜
      botOrder: [],     // chatbot的实际顺序

      state: 0,         // 当前的状态，可参考状态转移图
      placeholder: '说句话吧...',
      buttonName: '结束对话',
      rankTitle: '总排行榜',
      inputDisabled: false,

      introVisable: false,
      rankVisible: false,

      prompt: '',
      promptVisible: false,
    }
  },
  created() {
    if (window.navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i))
      this.isPhone = true
    if (navigator.userAgent.toLowerCase().match(/MicroMessenger/i) == "micromessenger") {
    } else {
      // 获取机器人列表
      http.post('/backend/bot').then(res => {
        this.botList = res.data.bot_list
        this.introVisable = true
      })
      this.openid = '网页匿名用户'
    }
  },
  watch: {
    state (newData, oldData) {
      switch (newData) {
        case 0:
          if (this.sessionId == '')
            this.placeholder = '说句话吧...'
          else
            this.placeholder = '对选定的气泡进行回复吧'
          this.inputDisabled = false
          this.buttonName = '结束对话'
          break
        case 1:
          this.placeholder = '等待对话模型的回复...'
          this.inputDisabled = true
          break
        case 2:
          this.placeholder = '请点击任一气泡进行回复...'
          break
        case 3:
          this.placeholder = '点击重新开始可进行新一轮对话'
          this.inputDisabled = true
          this.buttonName = '重新开始'
          break
      }
    }
  },
  methods: {
    clickEnter(e) {
      if (e.keyCode == 13)
        this.sendMsg()
    },
    async addMsg(msg) {
      this.msgList.push(msg)
      await nextTick()
      this.$refs.scrollbarRef.setScrollTop(this.$refs.innerRef.clientHeight)
    },
    async sendMsg() {
      if (this.msg == '')
        return
      this.addMsg({direction: 'right', content: this.msg})
      this.chatContext.push(this.msg)  // 将消息添加到上下文
      this.msg = ''
      this.state = 1
      // 向后端发送消息
      const data = {
        'session_id': this.sessionId,
        'openid': this.openid,
        'msg_send': this.chatContext
      }
      http.post('/backend/msg', data).then(res => {
        if (res.data.status == 'success') {
          this.sessionId = res.data.session_id
          let botMsg = {"direction": 'left', "contentList": []}
          for (let msg_received of res.data.msg_list_received)
            botMsg.contentList.push({"content": msg_received, "chosen": false})
          this.addMsg(botMsg)
          this.state = 2
        } else {
          this.popMessage('error', '当前无法获取部分机器人的回复，请稍后重试')
          this.msgList.pop()
          this.chatContext.pop()
          this.state = 0
        }
      })
    },
    clickButton() {
      if (this.chatContext.length == 0) {
        this.popMessage('warning', '您当前未发送任何消息')
      } else if (this.state == 1) {
        this.popMessage('warning', '请等待bot回复后再结束对话')
      } else if (this.state == 3) {
        this.popMessage('success', '开始新一轮对话吧！')
        this.sessionId = ''
        this.msg = ''
        this.msgList = []
        this.state = 0
        this.chatContext = []
        this.placeholder = '说句话吧...'
        this.botOrder = []
      } else {
        ElMessageBox.confirm('您是否要结束本轮对话？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(() => {
          this.state = 3
          http.post('/backend/order', {"session_id": this.sessionId}).then(res => {
            this.botOrder = res.data.bot_order
            // 弹出排行榜
            this.showRank(this.sessionId)
          })
        })
      }
    },
    clickBubble(i, j) {
      if ((this.state == 0 || this.state == 2) && i + 1 == this.msgList.length) {
        for (let k = 0; k < this.msgList[i].contentList.length; k++)
          this.msgList[i].contentList[k].chosen = false
        this.msgList[i].contentList[j].chosen = true
        if (this.state == 2) {
          this.state = 0
          this.chatContext.push(this.msgList[i].contentList[j].content)
        } else {
          this.chatContext[this.chatContext.length - 1] = this.msgList[i].contentList[j].content
        }
        // 更新数据库中被选择的信息
        const data = {
          'session_id': this.sessionId,
          'chosen_msg_index': j
        }
        http.post("/backend/choose", data)
      }
    },
    showRank(id = '')  {
      if (this.placeholder != '说句话吧...' &&
        this.placeholder != '点击重新开始可进行新一轮对话') {
        this.popMessage('warning', '若想查看排行榜，请先结束本轮会话')
      } else {
        if (id == '')
          this.rankTitle = '总排行榜'
        else
          this.rankTitle = '本轮排行'
        http.post('/backend/rank', {'session_id': id}).then(res => {
          this.rankList = res.data.rank_list
          this.rankVisible = true
        }) 
      }
    },
    closeRank() {
      if (this.botOrder.length != 0)
        this.popMessage('success', '点击重新开始可开启新一轮对话')
    },
    popMessage(type, msg) {
      ElMessage({
        type: type,
        message: msg,
      })
    },
    getPrompt() {
      if (this.msgList.length == 0) {
        http.post('/backend/prompt').then(res => {
          this.prompt = res.data.prompt
          this.promptVisible = true
        })
      } else {
        this.popMessage('warning', '当前对话已经开始，无法获取提示')
      }
    },
    sendPrompt() {
      this.msg = this.prompt
      this.sendMsg()
      this.promptVisible = false
    }
  },
  components: {
    Histogram, SwitchButton, RefreshRight, Promotion, Opportunity
  }
}
</script>

<template>
  <div class="container">
    <div class="header">
      <span class="title">
        在线机器人：
        <span v-for="(bot, i) in botList" :key="i">
          <el-tooltip placement="bottom">
            <template #content>
              <text style="white-space: pre-line">{{ bot['intro'] }}</text>
            </template>
            <span style="font-size: 18px;">
              {{ bot['short'] }}&nbsp;
            </span>
          </el-tooltip>
        </span>
      </span>
    </div>
    <div class="main" :style="isPhone ? 'height: calc(100vh - 64px - 40px)' : 'height: calc(80vh - 64px - 40px)'">
      <el-scrollbar ref="scrollbarRef">
        <div ref="innerRef">
          <div v-for="(msg, i) in msgList" :key="i">
            <div v-if="msg.direction=='right'" class="bubble right" style="margin-top: 15px">
              <span class="bubble-right">
                <div class="msg right">{{ msg.content }}</div>
              </span>
              <img class="avatar right" src="../assets/images/user.png"/>
            </div>
            <div v-else class="bubble-whole" style="margin-top: 15px; margin-bottom: 15px;">
              <div v-for="(content, j) in msg.contentList" :key="j" class="bubble left" @click="clickBubble(i, j)">
                <div class="avatar left" :style="content.chosen ? 'background-color: #01B99B; color: #fff' : ''">
                  {{ botOrder.length > 0 ? botOrder[parseInt(i / 2)][j][0] : String.fromCharCode(65 + j) }}
                </div>
                <span class="bubble-left" :style="content.chosen ? 'background-color: #01B99B;' : ''">
                  <div class="msg left" :style="content.chosen ? 'color: #fff' : ''">
                    {{ content.content }}</div>
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
    <div class="footer">
      <div style="margin-left: 8px; display: flex; position: relative; top: 3px;">
        <el-button @click="showRank()" size="small" type="info" plain round>
          <template #icon>
            <el-icon :size="14"><Histogram /></el-icon>
          </template>
          排行榜
        </el-button>
        <el-button @click="getPrompt()" size="small" type="warning" plain round>
          <template #icon>
            <el-icon :size="14"><Opportunity /></el-icon>
          </template>
          话题提示
        </el-button>
        <el-button @click="clickButton" size="small" :type="state != 3 ? 'danger' : 'success'" plain round>
          <template #icon>
            <el-icon :size="14">
              <div v-if="state != 3"><SwitchButton/></div>
              <div v-else><RefreshRight/></div>
            </el-icon>
          </template>
          {{ buttonName }}
        </el-button>
      </div>
      <div style="display: flex; position: relative; top: 5px;">
        <el-input v-model="msg" :placeholder="placeholder" class="input"
          @keydown.enter.native="clickEnter" :disabled="inputDisabled">
        </el-input>
        <el-button type="primary" class="send" @click="sendMsg" :disabled="inputDisabled" circle>
          <template #icon>
            <el-icon :size="18"><Promotion /></el-icon>
          </template>
        </el-button>
      </div>
    </div>
    <!-- 排行榜 -->
    <el-dialog v-model="rankVisible" :title="rankTitle" width="300px" @closed="closeRank()" center>
      <el-table :data="rankList" :stripe="true">
        <el-table-column align="left" label="对话模型排名" width="185px">
          <template #default="scope">
            <div style="display:flex">
              <span style="width: 25px;">{{ rankList.indexOf(scope.row) + 1 }}.</span>
              <div class="avatar gen" style="background-color: grey; color: #fff; margin-right: 7px;">
                {{ scope.row.bot_name[0] }}
              </div>
              &nbsp;{{ scope.row.bot_name == 'Finetune' ? 'GLM-Finetune' : scope.row.bot_name}}
            </div>
          </template>  
        </el-table-column>
        <el-table-column align="center" property="chosen_num" label="得分"/>
      </el-table>
    </el-dialog>
    <!-- 平台介绍 -->
    <el-dialog title="聊天机器人竞技场" :show-close="false" :close-on-press-escape="false"
      :close-on-click-modal="false" v-model="introVisable" :width="isPhone ? '90%' : '40%'" center>
      1. 在本平台，您可以和多个匿名聊天机器人同时对话，每输入一句话，平台都会提供若干个聊天机器人的回复。<br/>
      <br/>
      2. 机器人回复后，您可以点击任一气泡，针对您选择的气泡进行回复，与多个机器人继续对话。<br/>
      <br/>
      3. 当您不想继续聊天时，可以点击"结束对话"，对话结束后，平台将显示本轮对您对话的机器人名称，及本轮的排行榜。点击重新开始可开始新一轮对话。<br/>
      <br/>
      4. 在对话开始前，当您未发送任何消息时，点击"话题提示"可自动为您发送第一条消息，开始新一轮聊天。
      <template #footer>
        <el-button type="primary" @click="(introVisable = false)">确 定</el-button>
      </template>
    </el-dialog>
    <!-- 消息提示 -->
    <el-dialog v-model="promptVisible" title="主题提示" :width="isPhone ? '90%' : '40%'">
      <div>提示语句为：{{ prompt }}</div>
      <br/>
      <div>点击"刷新"获取其他提示语句，点击"确定"发送当前语句</div>
      <template #footer>
        <span>
          <el-button @click="getPrompt()">刷新</el-button>
          <el-button type="primary" @click="sendPrompt()">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
div span {
  font-family: "STHeiti Light";
  color: #2D2D2D;
}

/* 移动端 */
@media (max-width: 675px) {
  .container {
    width: 100%;
    height: calc(100vh);
  }
}

/* 电脑端 */
@media (min-width: 675px) {
  .container {
    height: calc(80vh);
    margin: calc(10vh) calc((100vw - 80vh * 16 / 12) / 2);
    border: 1px solid rgb(214, 214, 214);
    box-shadow: 3px 3px 5px #adadad;
    border-radius: 5px;
  }
}

.header {
  width: 100%;
  height: 40px;
}

.title {
  font-size: 18px;
  margin-left: 15px;
  line-height: 40px;
}

.main {
  width: 100%;
  /* height: 82%; */
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: inset 0px 7px 8px -12px #000,
    inset 0px -7px 8px -12px #000;
}

.footer {
  width: 100%;
  height: 62px;
  display: flex;
  flex-direction: column;
}

.input {
  align-self: center;
  margin: 0 10px 0 8px;
}

.send {
  align-self: center;
  margin-right: 8px;
}

.bubble {
  margin: 10px 0px;
  border-width: 0 12px;
  display: -webkit-flex;
  display: flex;
  -webkit-align-items: top;
  align-items: top;
}
.bubble.left {
  margin-left: 12px;
}
.bubble.right {
  -webkit-justify-content: flex-end;
  justify-content: flex-end;
  margin-right: 12px;
}
.bubble-left {
  width: calc(100% - 42px - 15px);
  padding: 5px 7px;
  margin-left: 10px;
  border-radius: 5px;
  background-color: #fff;
}
.bubble-right {
  padding: 5px 7px;
  margin-right: 10px;
  border-radius: 9px 9px 0px 9px;
  background-color: #088AF2;
}
.bubble-whole {
  margin: 0 40px 0 12px;
  padding: 5px 0;
  border-radius: 9px 9px 9px 0px;
  background-color: #F7F7F7;
}

.avatar {
  border-radius: 20px;
  box-shadow: 1px 2px 4px 0px rgb(185, 185, 185);
  z-index: 1;
}

.avatar.gen {
  text-align: center;
  height: 20px;
  width: 20px;
  line-height: 20px;
  font-size: 10px;
  color: #2D2D2D;
  position: relative;
  top: 1px;
}
.avatar.left {
  display: inline-block;
  text-align: center;
  height: 20px;
  width: 20px;
  line-height: 20px;
  font-size: 10px;
  color: #2D2D2D;
  position: relative;
  top: 4px;
}
.avatar.right {
  height: 28px;
  width: 28px;
}
.msg {
  font-size: 13px;
  line-height: 20px;
}
.msg.left {
  color: #2D2D2D;
}
.msg.right {
  max-width: calc(100vw - 72px - 50px);
  color: #fff;
  position: relative;
  left: 1px;
}
</style>
