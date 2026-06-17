import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles.css'
import App from './App.vue'
import { pinia } from './stores/pinia'

createApp(App).use(pinia).use(ElementPlus).mount('#app')
