import { defineStore } from "pinia"
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from "vue-router"

export const useAccountStore = defineStore('accounts', () => {
    const API_URL = 'http://127.0.0.1:8000'
    const router = useRouter()

    const signUp = function(payload) {
        const username = payload.username
        // const email = payload.email
        const password1 = payload.password1
        const password2 = payload.password2
        // const phonenumber = payload.phonenumber
        // const gender = payload.gender
    axios({
        method : 'post',
        url: `${API_URL}/accounts/registration/`,
        data: {
            username,
            // email,
            password1,
            password2,
            // phonenumber,
            // gender
        }
    })
        .then(res => {
            console.log('회원가입이 완료되었습니다.')
            logIn({username, password1})
        })
        .catch(err => console.log(err))
    }

    const token = ref(null)

    const logIn = function(payload){
        const username = payload.username
        const password = payload.password

        axios({
            method: 'post',
            url : `${API_URL}/accounts/login/`,
            data : {
                username, password
            }
        })
            .then(res => {
                console.log('로그인이 완료되었습니다.')
                console.log(res.data)
                token.value = res.data.key
                router.push({name:'MainView'})
            })
            .catch(err => console.log(err))

    }
    return {signUp, logIn, token}
}, {persist : true})