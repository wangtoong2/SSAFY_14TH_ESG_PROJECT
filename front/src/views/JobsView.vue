<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton title="구인구직 사이트 모음" main />

      <div class="grid grid-cols-1 gap-4 mt-6">
        <CardBox v-for="site in sites" :key="site.label" class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold"><a :href="site.href" target="_blank" rel="noopener" class="hover:underline">{{ site.label }}</a></h3>
              <div class="text-sm text-gray-500">{{ site.description }}</div>
            </div>
            <div>
              <a :href="site.href" target="_blank" rel="noopener" class="px-3 py-1 border rounded">바로가기</a>
            </div>
          </div>
        </CardBox>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

const sites = [
  { label: '사람인', href: 'https://www.saramin.co.kr/', description: '국내 대표 구인구직 플랫폼' },
  { label: '원티드', href: 'https://www.wanted.co.kr/', description: '추천 기반 채용 플랫폼' },
  { label: '잡코리아', href: 'https://www.jobkorea.co.kr/', description: '기업별 공고와 취업정보' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com/', description: '국제적 비즈니스 네트워크' },
]
</script>

<style scoped></style>
