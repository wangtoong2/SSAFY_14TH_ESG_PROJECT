<script setup>
import { computed, ref, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'
import {
  mdiAccountMultiple,
  mdiCartOutline,
  mdiChartTimelineVariant,
  mdiMonitorCellphone,
  mdiReload,
  // mdiGithub,
  mdiChartPie,
} from '@mdi/js'
import * as chartConfig from '@/components/Charts/chart.config.js'
import LineChart from '@/components/Charts/LineChart.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBoxWidget from '@/components/CardBoxWidget.vue'
import CardBox from '@/components/CardBox.vue'
import TableSampleClients from '@/components/TableSampleClients.vue'
import NotificationBar from '@/components/NotificationBar.vue'
import BaseButton from '@/components/BaseButton.vue'
import CardBoxTransaction from '@/components/CardBoxTransaction.vue'
import CardBoxClient from '@/components/CardBoxClient.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
// import SectionBannerStarOnGitHub from '@/components/SectionBannerStarOnGitHub.vue'
import { useRouter } from 'vue-router'
import ArticleList from '@/components/ArticleList.vue'

const router = useRouter()

const chartData = ref(null)

const fillChartData = () => {
  chartData.value = chartConfig.sampleChartData()
}

onMounted(() => {
  fillChartData()
})

const mainStore = useMainStore()

const clientBarItems = computed(() => mainStore.clients.slice(0, 4))

const transactionBarItems = computed(() => mainStore.history)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="주간 추천 기업" main>
        <BaseButton
          :icon="mdiGithub"
          label="글쓰기"
          color="contrast"
          rounded-full
          small
          @click="router.push({name : 'Create'})"
        />
      </SectionTitleLineWithButton>
<!-- 상단바  -->


      <div class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <CardBoxWidget
          trend="12%"
          trend-type="up"
          color="text-emerald-500"
          :icon="mdiAccountMultiple"
          :number="512"
          label="기업 이름추가"
        />
        <CardBoxWidget
          trend="12%"
          trend-type="down"
          color="text-blue-500"
          :icon="mdiCartOutline"
          :number="7770"
          prefix="$"
          label="기업 이름추가"
        />
        <CardBoxWidget
          trend="Overflow"
          trend-type="alert"
          color="text-red-500"
          :icon="mdiChartTimelineVariant"
          :number="256"
          suffix="%"
          label="기업 이름추가"
        />
      </div>

      <div class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="flex flex-col justify-between">
          <CardBoxTransaction
            v-for="i in 2" 
            :key="'trans-' + i"
            amount="0.00"
            date="날짜 표시"
            business="비즈니스명"
            type="deposit"
            name="계좌명"
            account="00000000"
          />
        </div>

        <div class="flex flex-col justify-between">
          <CardBoxClient
            v-for="i in 2" 
            :key="'client-' + i"
            name="고객명"
            login="아이디"
            date="2025-01-01"
            progress="0"
          />
        </div>
      </div>


      <SectionTitleLineWithButton :icon="mdiChartPie" title="기업 추천 바로가기">
      </SectionTitleLineWithButton>
      <CardBox class="mb-6">
        <h2>라우터링크 연결하기</h2>
      </CardBox>
      

      <!-- <SectionTitleLineWithButton :icon="mdiChartPie" title="Trends overview">
        <BaseButton :icon="mdiReload" color="whiteDark" @click="fillChartData" />
      </SectionTitleLineWithButton> -->

      <!-- <CardBox class="mb-6">
        <div v-if="chartData">
          <line-chart :data="chartData" class="h-96" />
        </div>
      </CardBox> -->

      <SectionTitleLineWithButton :icon="mdiAccountMultiple" title="게시글" />
      <ArticleList />
    </SectionMain>
  </LayoutAuthenticated>
</template>
