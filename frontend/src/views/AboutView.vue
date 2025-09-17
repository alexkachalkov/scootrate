<template>
  <div class="section">
    <div class="container">
      <h1>Как работает рейтинг</h1>
      <p>
        Top Scoot собирает результаты официальных и локальных соревнований за последние 90 дней. Каждому месту начисляется фиксированное количество очков, умноженное на коэффициент уровня турнира. Если участников больше 30 или 60 — очки получают бонус +10% или +20% соответственно. Суммарно за сезон райдер может набрать не более 1000 очков.
      </p>

      <h2>Таблица очков</h2>
      <table class="points-table">
        <thead>
          <tr>
            <th>Уровень турнира</th>
            <th>1 место</th>
            <th>2 место</th>
            <th>3 место</th>
            <th>Финалист</th>
            <th>Участник</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Международный</td>
            <td>400</td><td>300</td><td>220</td><td>100</td><td>20</td>
          </tr>
          <tr>
            <td>Национальный</td>
            <td>300</td><td>220</td><td>160</td><td>80</td><td>15</td>
          </tr>
          <tr>
            <td>Региональный</td>
            <td>200</td><td>140</td><td>100</td><td>50</td><td>10</td>
          </tr>
          <tr>
            <td>Локальный</td>
            <td>120</td><td>80</td><td>60</td><td>30</td><td>5</td>
          </tr>
        </tbody>
      </table>

      <h2>Что считается финалистом</h2>
      <p>
        По умолчанию финалист — это место с 4 по 8. Если у турнира свой формат (например, финал-12), организатор может указать это при публикации. Статус «участник» получают все, кто выступил в основной сетке.
      </p>

      <h2>Источники данных</h2>
      <p>
        Мы учитываем только опубликованные протоколы. Если заметите ошибку — сообщите через форму контактов. После проверки администратор поправит данные, а все изменения фиксируются в журнале аудита.
      </p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.section {
  padding: 50px 0 80px;
  line-height: 1.7;
  background: #fff;
}

.container {
  max-width: 860px;
  margin: 0 auto;
  padding: 0 24px;
}

h1 {
  margin-bottom: 20px;
}

h2 {
  margin-top: 32px;
  margin-bottom: 12px;
}

.points-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.points-table th,
.points-table td {
  border: 1px solid #e0e0e0;
  padding: 10px 14px;
  text-align: center;
}

.points-table th {
  background: #f5f5f5;
}
</style>
