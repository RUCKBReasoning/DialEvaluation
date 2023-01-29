<template>
  <div class="container">
    <div class="header">
      <div style="position: relative; top: 50%; transform: translateY(-50%);">
        <span class="title" style="align-self:left">用户名：{{ annotatorName }}</span>
        <span id="chatNum" class="title" :style="chatNum < roundRequired ? 'color: #9D1515;' : 'color: #008000;'">
          当前对话轮数：{{ chatNum }}
        </span>
        <br class="pcmobilebreak">
        <span id="taskNum" class="title" style="color: #9D1515;">
          剩余任务数：{{ taskNum }}
        </span>
        <div style="float: right">
          <el-tooltip class="box-item" effect="dark" placement="left-start">
            <template #content>
              对话基本要求：<br/>
              1. 消息不能太短，平均10个字以上<br/>
              2. 整个对话尽量限制在与起始语句相关的话题当中<br/>
              3. 消息中不能有敏感词、反动言语、侮辱性言语等<br/> 
              4. 消息中应包含一定的信息量
            </template>
            <el-button class="send" circle>
              <template #icon> 
                <el-icon :size="18"><QuestionFilled/></el-icon>
              </template>
            </el-button>
          </el-tooltip>
        </div>
        <el-button class="send" style="float: right;" @click="refresh()" round>
          重新开始
          <template #icon> 
            <el-icon :size="18"><Refresh/></el-icon>
          </template>
        </el-button>
      </div>
    </div>
    <div class="main">
      <el-scrollbar ref="scrollbarRef">
        <div ref="innerRef">
          <div v-for="(msg, i) in msgList" :key="i">
            <div id="msgRight" v-if="i % 2 == 0" class="bubble right" style="margin-top: 15px">
              <span class="bubble-right">
                <div class="msg right">{{ msg }}</div>
              </span>
              <img class="avatar" src="../assets/user.png"/>
            </div>
            <div  id="msgLeft" v-else class="bubble left" style="margin-top: 15px" >
              <img class="avatar" src="../assets/robot.png"/>
              <span class="bubble-left">
                <div class="msg left">{{ msg }}</div>
              </span>
            </div>  
          </div>
        </div>
      </el-scrollbar>
    </div>
    <div class="footer">
      <el-button class="send" @click="clickUpload()" round>
        上传
        <template #icon> 
          <el-icon :size="18"><Upload/></el-icon>
        </template>
      </el-button>
      <el-input v-model="msg" :placeholder="placeholder" class="input"
        @keydown.enter="clickEnter" :disabled="inputDisabled">
      </el-input>
      <el-button type="primary" class="send" @click="sendMsg()" :disabled="inputDisabled" circle>
        <template #icon>
          <el-icon :size="18"><Promotion /></el-icon>
        </template>
      </el-button>
    </div>
  </div>
</template>

<script>
import { Upload, QuestionFilled, Promotion, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useStore } from '../store/index'
import http from '@/utils/http'
import { nextTick } from 'vue'

export default {
  name: 'EvalRoom',
  data() {
    return {
      msg: '',
      annotatorName: '',
      annotatorId: '',
      chatGenerationId: '',
      msgList: [],

      taskNum: '',
      chatColor: 'red',
      taskColor: 'red',

      state: 0,
      inputDisabled: false,
      placeholder: '说句话吧...',

      roundRequired: 5,
    }
  },
  computed: {
    chatNum() {
      return parseInt(this.msgList.length / 2)
    }
  },
  watch: {
    state (newData) {
      switch (newData) {
        case 0:
          this.placeholder = '说句话吧...'
          this.inputDisabled = false
          break
        case 1:
          this.placeholder = '等待对话模型的回复...'
          this.inputDisabled = true
          break
        case 2:
          this.placeholder = '已达到上限，请上传或重新开始'
          this.inputDisabled = true
          break
      }
    }
  },
  created() {
    const store = useStore()
    this.annotatorId = store.annotatorId
    this.annotatorName = store.annotatorName
    this.getNextChat()
  },
  methods: {
    clickUpload() {
      if (this.chatNum < this.roundRequired){
        this.msgBox('生成轮数不够，上传失败，请继续生成')
      } else {
        const data = {
          'chat_generation_id': this.chatGenerationId,
          'chat_content': this.msgList
        }
        http.post("/chat-anno/upload-generate", data).then(res => {
          if (res.data.state == 'success') {
            ElMessage({
              message: '成功上传生成结果',
              type: 'success',
            })
            this.reset()
            this.getNextChat()
          }
        })
      }
    },
    getNextChat() {
      const data = {'annotator_id': this.annotatorId}
      http.post("/chat-anno/next-generate", data).then(res => {
        this.taskNum = res.data.chat_num
        if (res.data.chat_num != 0) {
          this.chatGenerationId = res.data.chat_generation_id
          // 获取bot的回复
          this.msg = res.data.chat_record[0]
          this.sendMsg()
        } else {
          this.msgBox('您已完成所有对话生成')
        }
      })
    },
    refresh() {
      if (this.msgList.length % 2 == 1) {
        this.msgBox('请等待bot回复后再进行刷新')
        return
      }
      if (this.msgList.length > 2) {
        this.reset()
        this.getNextChat()
      }
    },
    reset() {
      this.msgList = []
      this.state = 0
    },
    msgBox(msg) {
      ElMessageBox.alert(msg, '提示', {
        confirmButtonText: '确定',
      })
    },
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
      this.state = 1
      const curMsg = this.msg
      this.msg = ""
      await this.addMsg(curMsg)
      // 获取bot的回复
      const data = {
        'chat_generation_id': this.chatGenerationId,
        'msg_send': this.msgList
      }
      http.post("/chat-anno/get-msg", data).then(async res => {
        if (res.data.state == 'success') {
          await this.addMsg(res.data.msg_received)
          if (this.chatNum == this.roundRequired)
            this.state = 2
          else
            this.state = 0
        } else {
          this.msgList.pop()
          this.msgBox('获取bot回复失败，请联系管理员')
        }
      })
    },
  },
  components: {
    Upload, QuestionFilled, Promotion, Refresh
  },
}
</script>

<style scoped>
div span {
  font-family: "STHeiti Light";
  font-size: 13px;
  color: #2D2D2D;
}
.container {
  width: 100%;
  height: calc(100vh);
}

.header {
  width: 100%;
  height: 9%;
}

.main {
  width: 100%;
  height: 83%;
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: inset 0px 7px 8px -12px #000,
    inset 0px -7px 8px -12px #000;
  position: relative; 
}

.footer {
  width: 100%;
  height: 8%;
  display: flex;
}

.title {
  font-size: 18px;
  margin-left: 15px;
}

.send {
  align-self: center;
  margin-right: 4px;
  margin-left: 4px;
}

.input {
  align-self: center;
  margin: 0 10px 0 8px;
}


/* message styling */
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
  padding: 5px 7px;
  margin-left: 10px;
  margin-right: 60px;
  border-radius: 0px 9px 9px 9px;
  background-color: #F3F3F3;
}
.bubble-right {
  padding: 5px 7px;
  margin-right: 10px;
  border-radius: 9px 9px 0px 9px;
  background-color: #088AF2;
}

.avatar {
  height: 28px;
  width: 28px;
  border-radius: 20px;
  box-shadow: 1px 2px 4px 0px rgb(185, 185, 185);
}
.msg {
  font-size: 13px;
  line-height: 20px;
  color: #fff;
}
.msg.left {
  color: #000;
}
.msg.right {
  max-width: calc(100vw - 72px - 50px);
  position: relative;
  left: 1px;
}

@media (min-width: 675px) {
  .pcmobilebreak {
    display: none !important;
  }
}
</style>