<template>
  <div class="flex gap-3">
    <button
      class="flex-1 btn-gold py-3 text-base touch-target"
      :disabled="!canFeedback"
      :class="{ 'opacity-40 cursor-not-allowed': !canFeedback }"
      @click="$emit('feedback', 'success')"
    >
      增幅成功
    </button>
    <button
      class="flex-1 btn-red py-3 text-base touch-target"
      :disabled="!canFeedback"
      :class="{ 'opacity-40 cursor-not-allowed': !canFeedback }"
      @click="$emit('feedback', 'failure')"
    >
      增幅失败
    </button>
  </div>
  <p v-if="!canFeedback" class="text-xs text-gray-500 mt-1 text-center">
    记录至少 10 次垫手结果后可反馈
  </p>
</template>

<script setup>
defineProps({
  canFeedback: { type: Boolean, default: false }
})

defineEmits(['feedback'])
</script>