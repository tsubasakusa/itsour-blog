<template>
  <div class="about-page">
    <div class="section-header">
      <span class="section-line"></span>
      <h2>PEOPLE</h2>
      <span class="section-line"></span>
    </div>
    <div class="about-content">
      <p>關於「人」的頁面。</p>
    </div>
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.section-header h2 {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 4px;
  white-space: nowrap;
}

.section-line {
  flex: 1;
  height: 1px;
  background: #000;
}

.about-content {
  font-family: Georgia, serif;
  font-size: 18px;
  line-height: 1.8;
}
</style>
