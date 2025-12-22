<script setup>
import { reactive,ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiAccount, mdiMail, mdiAsterisk, mdiFormTextboxPassword, mdiGithub } from '@mdi/js'
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

const accountStore = useAccountStore()

const mainStore = useMainStore()

const profileForm = reactive({
  name: mainStore.userName,
  email: mainStore.userEmail,
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
const submitProfile = () => {
  // 프로필 정보를 mainStore에 저장
  mainStore.setUser(profileForm)
  console.log('프로필 업데이트:', profileForm)
}

// 비밀번호 변경 제출 함수
const submitPass = () => {
  // 비밀번호 변경 로직 작성 예정
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


const withdraw = () => {
  accountStore.withdraw()
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccount" title="Profile" main>
        <BaseButton
          href="https://github.com/justboil/admin-one-vue-tailwind"
          target="_blank"
          :icon="mdiGithub"
          label="Star on GitHub"
          color="contrast"
          rounded-full
          small
        />
      </SectionTitleLineWithButton>

      <UserCard class="mb-6" />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CardBox is-form @submit.prevent="submitProfile">
          <FormField label="Avatar" help="Max 500kb">
            <FormFilePicker label="Upload" />
          </FormField>

          <FormField label="Name" help="Required. Your name">
            <FormControl
              v-model="profileForm.name"
              :icon="mdiAccount"
              name="username"
              required
              autocomplete="username"
            />
          </FormField>
          
          <FormField label="E-mail" help="Required. Your e-mail">
            <FormControl
              v-model="profileForm.email"
              :icon="mdiMail"
              type="email"
              name="email"
              required
              autocomplete="email"
            />
          </FormField>

          <FormField label="Phone-number" help="-를 제외하고 입력해주세요">
            <FormControl
              v-model="profileForm.phonenumber"
              :icon="mdiphone"
              type="tel"
              name="phonenumber"
              required
              autocomplete="tel"
              placeholder="예: 01012345678"
            />
          </FormField>

          <FormField label="Gender" help="Required. Please select your gender.">
            <div class="gender-options">
              <!-- 남자 라디오 버튼 -->
              <label>
                <input 
                  type="radio"
                  v-model="profileForm.gender"
                  value="male"
                  name="gender"
                  required
                >
                남자
              </label>
              <!-- 여자 라디오 버튼 -->
              <label>
                <input type="radio" 
                v-model="profileForm.gender"
                value ="female" 
                name="gender"
                required>
                여자
              </label>
            </div>
          </FormField>
          <BaseDivider />
          <FormField label="Interest" help="취업 희망 분야를 선택해주세요">
            <div>
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
              <BaseButton color="info" label="Options" outline />
            </BaseButtons>
          </template>
        </CardBox>


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
          <BaseButton type="submit" color="info" label="Submit" />
          
          <BaseDivider />
          
        
          <!-- <template #footer>
            <BaseButtons>
              <BaseButton type="submit" color="info" label="Submit" />
              <BaseButton color="info" label="Options" outline />
            </BaseButtons>
          </template> -->
        </CardBox>
      </div>
      <CardBox>
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