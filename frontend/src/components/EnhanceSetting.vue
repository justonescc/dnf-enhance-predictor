<template>
  <div class="card">
    <h2 class="text-lg font-bold text-dnf-gold mb-3">增幅设置</h2>

    <div class="space-y-3">
      <!-- 目标增幅等级 -->
      <div>
        <label class="block text-sm text-gray-400 mb-1">目标增幅等级</label>
        <select
          :value="enhanceLevel"
          @change="$emit('update:enhanceLevel', $event.target.value)"
          class="w-full bg-dnf-dark border border-dnf-card rounded-lg px-3 py-2 text-white focus:border-dnf-gold focus:outline-none touch-target"
        >
          <option v-for="level in enhanceLevels" :key="level" :value="level">
            {{ level }} (成功率 {{ (rates[level] * 100).toFixed(0) }}%)
          </option>
        </select>
      </div>

      <!-- 徽章等级 -->
      <div>
        <label class="block text-sm text-gray-400 mb-1">垫手徽章等级</label>
        <select
          :value="badgeLevel"
          @change="$emit('update:badgeLevel', Number($event.target.value))"
          class="w-full bg-dnf-dark border border-dnf-card rounded-lg px-3 py-2 text-white focus:border-dnf-gold focus:outline-none touch-target"
        >
          <option v-for="lv in badgeLevels" :key="lv" :value="lv">
            {{ lv }}级 (合成成功率 {{ (badgeRates[lv] * 100).toFixed(0) }}%)
          </option>
        </select>
      </div>

      <!-- 基础成功率显示 -->
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-400">垫手基础成功率</span>
        <span class="text-dnf-gold font-bold">{{ (badgeRates[badgeLevel] * 100).toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ENHANCE_RATES, BADGE_RATES } from '../services/api.js'

defineProps({
  enhanceLevel: { type: String, default: '+10' },
  badgeLevel: { type: Number, default: 7 }
})

defineEmits(['update:enhanceLevel', 'update:badgeLevel'])

const rates = ENHANCE_RATES
const badgeRates = BADGE_RATES

const enhanceLevels = [
  '+4', '+5', '+6', '+7', '+8', '+9', '+10',
  '+11', '+12', '+13', '+14', '+15', '+16', '+17', '+18', '+19'
]

const badgeLevels = [5, 6, 7, 8, 9, 10]
</script>
