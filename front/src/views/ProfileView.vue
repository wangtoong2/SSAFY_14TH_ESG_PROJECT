<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiAccount, mdiMail, mdiAsterisk, mdiFormTextboxPassword, mdiGithub, mdiPhone } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import FormFilePicker from '@/components/FormFilePicker.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import UserCard from '@/components/UserCard.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import { useAccountStore } from '@/stores/accounts'
import axios from 'axios'

const accountStore = useAccountStore()

const mainStore = useMainStore()

const avatarFile = ref(null)
const selectedAvatar = ref(null)
const selectedAvatarPreview = ref(null)

const isSocialUser = ref(false)

const onAvatarChange = (file) => {
  // clear
  if (!file) {
    if (selectedAvatarPreview.value && selectedAvatarPreview.value.startsWith('blob:')) {
      URL.revokeObjectURL(selectedAvatarPreview.value)
    }
    selectedAvatar.value = null
    selectedAvatarPreview.value = null
    return
  }

  // revoke previous blob preview
  if (selectedAvatarPreview.value && selectedAvatarPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(selectedAvatarPreview.value)
  }

  selectedAvatar.value = file // keep File for upload
  const url = URL.createObjectURL(file)
  selectedAvatarPreview.value = url // show preview locally

  // DEBUG: 아바타 파일 선택/프리뷰 URL 생성 확인용 로그
  // console.log('선택된 아바타(미저장 프리뷰):', file, url)
}

const avatarPreview = computed(() => {
  // prefer unsaved local preview, otherwise use store value
  return selectedAvatarPreview.value || mainStore.userAvatarUrl || null
})

const uploadAvatar = async () => {
  if (!selectedAvatar.value) return

  const formData = new FormData()
  formData.append('avatar', selectedAvatar.value)

  try {
    const res = await axios.patch(
      'http://127.0.0.1:8000/accounts/user/avatar/',
      formData,
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    // revoke local blob preview if present
    if (selectedAvatarPreview.value && selectedAvatarPreview.value.startsWith('blob:')) {
      URL.revokeObjectURL(selectedAvatarPreview.value)
    }

    // sync stores with server value (res.data.avatar expected to be server path)
    mainStore.setUser({
      avatar: res.data.avatar,
    })
    accountStore.avatar = res.data.avatar
    selectedAvatar.value = null
    selectedAvatarPreview.value = null

    alert('아바타가 변경되었습니다.')
  } catch (e) {
    console.error(e)
    alert('아바타 업데이트에 실패했습니다.')
  }
}




const profileForm = reactive({
  nickname: '',
  email: '',
  phonenumber : mainStore.userPhonenumber || '',
  gender : mainStore.userGender || '',
  // || => 없으면 빈 문자열
  Interest: [], // 관심분야를 배열로 저장
})

// 비밀번호 폼
const passwordForm = reactive({
  password_current: '',
  password: '',
  password_confirmation: '',
})


// 프로필 업데이트 제출 함수
const submitProfile = async () => {
  try {
    const res = await axios.patch(
      'http://127.0.0.1:8000/accounts/user/',
      {
        nickname: profileForm.nickname,
        email: profileForm.email,
        phone_number: profileForm.phonenumber,
        gender: profileForm.gender,
        interests: profileForm.Interest,
      },
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    // 프론트 store 동기화
    // update nickname display and stores
    accountStore.nickname = res.data.nickname || ''
    accountStore.userName = res.data.username
    mainStore.setUser({
      name: res.data.nickname || res.data.username,
      email: res.data.email,
    })

    alert('프로필이 수정되었습니다.')
  } catch (err) {
    console.error(err.response?.data || err)
    alert('프로필 수정 실패')
  }
}


// 비밀번호 변경 함수
const submitPass = async () => {
  if (passwordForm.password !== passwordForm.password_confirmation) {
    alert('비밀번호가 일치하지 않습니다.')
    return
  }

  try {
    await axios.post(
      'http://127.0.0.1:8000/accounts/password/change/custom/',
      {
        old_password: passwordForm.password_current,
        new_password: passwordForm.password,
      },
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    alert('비밀번호가 변경되었습니다. 다시 로그인해주세요.')
    accountStore.logOut()
  } catch (err) {
    const data = err.response?.data

    if (data?.detail) {
      alert(data.detail)
    } else {
      alert('비밀번호 변경에 실패했습니다.')
    }

    console.error(data || err)
  }
}



// 관심분야 예시
const allInterests = [
  { id: 1, name: 'Software Engineering' },
  { id: 2, name: 'Data Science' },
  { id: 3, name: 'Product Management' },
  { id: 4, name: 'Marketing' },
  { id: 5, name: 'Design' },
  { id: 6, name: 'Business Analysis' },
  { id: 7, name: 'Artificial Intelligence' },
  { id: 8, name: 'Machine Learning' },
]

const searchQuery = ref('')  // 검색어를 저장하는 변수
const filteredInterests = ref(allInterests)  // 필터링된 관심 분야 목록
const fallbackInterests = ref([])  // 유사한 항목 목록

// 검색어에 맞는 결과를 필터링하는 함수
const filterResults = () => {
  if (searchQuery.value === '') {
    filteredInterests.value = allInterests
  } else {
    filteredInterests.value = allInterests.filter((interest) =>
      interest.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    // 검색어와 유사한 항목을 찾아서 보여주기
    fallbackInterests.value = allInterests.filter((interest) =>
      interest.name.toLowerCase().includes(searchQuery.value.toLowerCase()) === false &&
      interest.name.toLowerCase().indexOf(searchQuery.value.toLowerCase()) !== -1
    )
  }
}

const removeInterest = (interest) => {
  profileForm.Interest = profileForm.Interest.filter(
    i => i !== interest
  )
}


const withdraw = () => {
  accountStore.withdraw()
}

onMounted(async () => {
  // DEBUG: 프로필 로드 전 이메일 값 확인용 로그
  // console.log('EMAIL:', profileForm.email, typeof profileForm.email)
  try {
    const res = await axios.get(
      'http://127.0.0.1:8000/accounts/user/',
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    isSocialUser.value = !!res.data.is_social

    // 1️⃣ form 채우기
    profileForm.nickname = res.data.nickname || res.data.username
    profileForm.email = res.data.email
    profileForm.phonenumber = res.data.phone_number || ''
    profileForm.gender = res.data.gender || ''
    profileForm.Interest = res.data.interests || []

    // 2️⃣ store 동기화 (중요)
    accountStore.userName = res.data.username
    accountStore.nickname = res.data.nickname || ''
    mainStore.setUser({
      name: res.data.nickname || res.data.username,
      email: res.data.email,
      userPhonenumber: res.data.phone_number,
      userGender: res.data.gender,
      avatar : res.data.avatar,
    })

  } catch (err) {
    console.error(err)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccount" title="Profile" main>

      </SectionTitleLineWithButton>

      <UserCard class="mb-6" />

      <div :class="isSocialUser ? 'grid grid-cols-1 gap-6' : 'grid grid-cols-1 gap-6 lg:grid-cols-2'">
        <!-- Left column: avatar + nickname -->
        <div>
          <div v-if="isSocialUser" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CardBox class="mb-0 w-full flex flex-col items-center">
              <FormField label="Avatar" help="Max 500kb">
                <FormFilePicker
                  label="Upload"
                  v-model="selectedAvatar"
                  accept="image/*"
                  @update:model-value="onAvatarChange"
                />
                <div v-if="avatarPreview" class="mt-3">
                  <img
                    :src="avatarPreview"
                    class="w-32 h-32 rounded-full object-cover object-center border"
                    style="width:128px;height:128px;"
                  />
                </div>
              </FormField>
              <button class="mt-2 px-4 py-1 bg-blue-500 text-white rounded" @click="uploadAvatar">
                아바타 저장
              </button>
            </CardBox>

            <CardBox is-form @submit.prevent="submitProfile" class="mb-0 w-full">
              <FormField label="Nickname" help="표시될 별명입니다">
                <FormControl
                  v-model="profileForm.nickname"
                  :icon="mdiAccount"
                  name="nickname"
                  autocomplete="nickname"
                />
              </FormField>
              <template #footer>
                <BaseButtons>
                  <BaseButton color="info" type="submit" label="닉네임 저장" />
                </BaseButtons>
              </template>
            </CardBox>
          </div>

          <template v-else>
            <CardBox class="mb-4 flex flex-col items-center">
              <FormField label="Avatar" help="Max 500kb">
                <FormFilePicker
                  label="Upload"
                  v-model="selectedAvatar"
                  accept="image/*"
                  @update:model-value="onAvatarChange"
                />
                <div v-if="avatarPreview" class="mt-3">
                  <img
                    :src="avatarPreview"
                    class="w-32 h-32 rounded-full object-cover object-center border"
                    style="width:128px;height:128px;"
                  />
                </div>
              </FormField>
              <button class="mt-2 px-4 py-1 bg-blue-500 text-white rounded" @click="uploadAvatar">
                아바타 저장
              </button>
            </CardBox>

            <CardBox is-form @submit.prevent="submitProfile">
              <FormField label="Nickname" help="표시될 별명입니다">
                <FormControl
                  v-model="profileForm.nickname"
                  :icon="mdiAccount"
                  name="nickname"
                  autocomplete="nickname"
                />
              </FormField>
              <template #footer>
                <BaseButtons>
                  <BaseButton color="info" type="submit" label="닉네임 저장" />
                </BaseButtons>
              </template>
            </CardBox>
          </template>
        </div>

        <!-- Right column: password box (hide for social login users) -->
        <div v-if="!isSocialUser">
          <CardBox is-form @submit.prevent="submitPass">
            <FormField label="현재 비밀번호" help="Required. Your current password">
              <FormControl
                v-model="passwordForm.password_current"
                :icon="mdiAsterisk"
                name="password_current"
                type="password"
                required
                autocomplete="current-password"
              />
            </FormField>

            <BaseDivider />

            <FormField label="새 비밀번호" help="Required. New password">
              <FormControl
                v-model="passwordForm.password"
                :icon="mdiFormTextboxPassword"
                name="password"
                type="password"
                required
                autocomplete="new-password"
              />
            </FormField>

            <FormField label="비밀번호 확인" help="Required. New password one more time">
              <FormControl
                v-model="passwordForm.password_confirmation"
                :icon="mdiFormTextboxPassword"
                name="password_confirmation"
                type="password"
                required
                autocomplete="new-password"
              />
            </FormField>
            <BaseButton type="submit" color="info" label="비밀번호 변경" />
          </CardBox>
        </div>
      </div>

      <!-- Full-width profile details form -->
      <CardBox is-form @submit.prevent="submitProfile" class="mt-6">
        <FormField label="E-mail" help="선택 사항">
          <FormControl
            :key="profileForm.email"
            v-model="profileForm.email"
            :icon="mdiMail"
            type="text"
            name="email"
            autocomplete="email"
          />
        </FormField>
        <FormField label="Phone-number" help="선택 사항 - `-` 제외">
          <FormControl
            v-model="profileForm.phonenumber"
            :icon="mdiPhone"
            type="tel"
            name="phonenumber"
            autocomplete="tel"
            placeholder="예: 01012345678"
          />
        </FormField>
        <FormField label="Gender" help="선택 사항">
          <div class="gender-options">
            <label>
              <input
                type="radio"
                v-model="profileForm.gender"
                value="male"
                name="gender"
              >
              남자
            </label>
            <label>
              <input type="radio"
                v-model="profileForm.gender"
                value="female"
                name="gender"
              >
              여자
            </label>
          </div>
        </FormField>
        <BaseDivider />
        <FormField label="Interest" help="선택 사항 - 관심분야를 선택하세요(선택적)">
            <div>
              <!-- 선택된 관심 분야 표시 -->
              <div
                v-if="profileForm.Interest.length"
                class="flex flex-wrap gap-2 mb-2"
              >
                <span
                  v-for="interest in profileForm.Interest"
                  :key="interest"
                  class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1"
                >
                  {{ interest }}
                  <button
                    type="button"
                    class="text-blue-500 hover:text-red-500"
                    @click="removeInterest(interest)"
                  >
                    ✕
                  </button>
                </span>
              </div>

              <!-- 검색 입력 필드 -->
              <input
                v-model="searchQuery"  
                @input="filterResults"  
                type="text"
                placeholder="검색어를 입력하세요..."
                class="input"
              />

              <!-- 검색어가 없을 때는 아무것도 보이지 않게 하기 -->
              <div v-if="searchQuery !== ''">
                <!-- 필터링된 관심 분야 선택 -->
                <div v-if="filteredInterests.length > 0">
                  <div v-for="interest in filteredInterests" :key="interest.id">
                    <label>
                      <input
                        type="checkbox"  
                        v-model="profileForm.Interest"  
                        :value="interest.name"  
                      />
                      {{ interest.name }}
                    </label>
                  </div>
                </div>
                <div v-else>
                  <p>검색된 결과가 없습니다. 유사한 분야를 확인하세요:</p>
                  <div v-for="interest in fallbackInterests" :key="interest.id">
                    <label>
                      <input
                        type="checkbox"
                        v-model="profileForm.Interest"
                        :value="interest.name"
                      />
                      {{ interest.name }}
                    </label>
                  </div>
                </div>
              </div>
              <!-- 검색어가 없을 때는 결과 숨기기 -->
              <div v-if="searchQuery === ''">
                <p>검색어를 입력하면 관심 분야 항목이 여기에 표시됩니다.</p>
              </div>
            </div>
          </FormField>

          

          <template #footer>
            <BaseButtons>
              <BaseButton color="info" type="submit" label="Submit" />
            </BaseButtons>
          </template>
        </CardBox>


      
      <CardBox style="margin-top:10px">
        <h2 class="text-lg font-semibold text-red-600 mb-4">
          회원탈퇴
        </h2>

        <p class="text-sm text-gray-500 mb-6">
          회원탈퇴 시 모든 정보가 삭제되며 복구할 수 없습니다.
        </p>

        <BaseButton
          color="danger"
          label="회원탈퇴"
          @click="withdraw"
        />
      </CardBox>

    </SectionMain>
  </LayoutAuthenticated>
</template>

<style>
  /* CSS로 라디오 버튼을 한 행에 나란히 배치 */
.gender-options label {
  display: inline-block;
  margin-right: 20px; /* 라디오 버튼 사이 간격 */
}

</style>