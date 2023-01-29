<template>
  <div class="container">
    <div class="header"></div>
    <div class="main"></div>
    <div class="footer">
      <el-dialog v-model="dialogVisible" title="对话系统标注平台" width="300px"
      :show-close="false" :close-on-press-escape="false" :close-on-click-modal="false" center>
        <el-form>
          <el-form-item label="账号">
            <el-input v-model="annotatorId" autocomplete="off" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="password" autocomplete="off" type="password"/>
          </el-form-item>
        </el-form>
        <span style="color: red">{{ loginMsg }}</span>
        <template #footer>
          <el-button type="primary" @click="checkLogin();">
            登录
          </el-button>
        </template> 
      </el-dialog>
    </div>
  </div>
</template>

<script>
import http from '@/utils/http'
import { useStore } from '../store/index'

export default {
  name: 'EvalRoom',
  data() {
    return {
      annotatorId: '',
      password: '',
      loginMsg: '',
      dialogVisible: true,
    }
  },
  methods: {
    checkLogin() {
      let data = {
        'annotator_id': this.annotatorId,
        'password': this.password
      }
      http.post("/chat-anno/login", data).then(res => {
        if (res.data.annotator_name != '') {
          const store = useStore()
          store.annotatorId = this.annotatorId
          store.annotatorName = res.data.annotator_name
          store.hasLogin = true
          if (res.data.annotator_role == 'evaluation')
            this.$router.replace({name: 'Eval'})
          else
            this.$router.replace({name: 'Gen'})
        } else {
          this.loginMsg = 'ID或密码错误，请重试'
        }
      })
    },
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
  height: 7%;
}

.main {
  width: 100%;
  height: 85%;
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
</style>