<script>
import ChatRoom from './components/ChatRoom.vue'

export default {
  name: "App",
  components: { ChatRoom }
}
</script>

<template>
  <div>
    <ChatRoom/>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
}

.el-input__wrapper {
  border-radius: 16px;
}
</style>
