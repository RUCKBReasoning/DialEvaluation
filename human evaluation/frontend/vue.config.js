const { defineConfig } = require('@vue/cli-service')
const AutoImport = require('unplugin-auto-import/webpack')
const Components = require('unplugin-vue-components/webpack')
const { ElementPlusResolver } = require('unplugin-vue-components/resolvers')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: './',
  outputDir: 'chat-anno-frontend',
  productionSourceMap: false,
  devServer: {
    // historyApiFallback: true,
    open: false,
    host: '127.0.0.1',
    port: 8080,
    https: false,
    proxy: {
      '/chat-anno': {
        target: 'http://192.168.5.8:10000/',
        changeOrigin: true,
        wa: true,
        pathRewrite: {
          '^/chat-anno': '',
        }
      },
    },
  },
  configureWebpack: {
    plugins: [
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
  }
})
