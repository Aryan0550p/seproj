<template>
  <section class="assistant-shell" :class="{ open: isOpen }">
    <button v-if="!isOpen" type="button" class="assistant-launcher" @click="isOpen = true">
      <span class="assistant-launcher-icon">AI</span>
      <span>Assistant</span>
    </button>

    <div v-else class="assistant-panel" role="dialog" aria-label="AI assistant">
      <header class="assistant-header">
        <div>
          <p class="assistant-eyebrow">YUMSIE AI</p>
          <h2>Smart helper</h2>
        </div>
        <button type="button" class="assistant-close" @click="isOpen = false" aria-label="Close assistant">&times;</button>
      </header>

      <div class="assistant-summary">
        <span>Role: {{ roleLabel }}</span>
        <span>Page: {{ currentRouteLabel }}</span>
      </div>

      <div ref="messagesPane" class="assistant-messages">
        <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
          <div class="bubble">{{ message.text }}</div>
        </article>
      </div>

      <div class="assistant-prompts">
        <button
          v-for="prompt in promptList"
          :key="prompt"
          type="button"
          class="prompt-chip"
          @click="sendPrompt(prompt)"
        >
          {{ prompt }}
        </button>
      </div>

      <form class="assistant-form" @submit.prevent="handleSubmit">
        <input
          v-model="draft"
          type="text"
          placeholder="Ask about users, inventory, orders, or navigation..."
          autocomplete="off"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  </section>
</template>

<script>
import { computed, nextTick, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getAllUsers, getUserRole } from '../auth'
import { getOrders, getProducts } from '../store'

export default {
  name: 'AiChatWidget',
  setup() {
    const route = useRoute()
    const isOpen = ref(false)
    const draft = ref('')
    const messagesPane = ref(null)
    const role = computed(() => getUserRole() || 'guest')
    const roleLabel = computed(() => role.value.charAt(0).toUpperCase() + role.value.slice(1))
    const currentRouteLabel = computed(() => route.name || 'Dashboard')
    const messages = ref([
      {
        id: 1,
        role: 'assistant',
        text: 'I can give live numbers from your current data. Ask for pending orders, payments, stock, users, or a KPI snapshot.'
      }
    ])

    const promptList = computed(() => {
      if (role.value === 'admin') {
        return ['Live KPI snapshot', 'Pending orders', 'Pending payments', 'Low stock products']
      }

      if (role.value === 'salesman') {
        return ['Live KPI snapshot', 'Pending orders', 'Pending payments', 'Delivered orders']
      }

      if (role.value === 'retailer') {
        return ['Live KPI snapshot', 'My pending orders', 'Pending payments', 'Delivered orders']
      }

      return ['Live KPI snapshot', 'Pending orders', 'Pending payments', 'Low stock products']
    })

    const scrollToLatest = async () => {
      await nextTick()
      if (messagesPane.value) {
        messagesPane.value.scrollTop = messagesPane.value.scrollHeight
      }
    }

    const addMessage = async (roleName, text) => {
      messages.value.push({
        id: Date.now() + Math.random(),
        role: roleName,
        text
      })
      await scrollToLatest()
    }

    const toCurrency = (amount) => `INR ${Math.round(amount).toLocaleString()}`

    const buildLiveMetrics = () => {
      const orders = getOrders()
      const products = getProducts()
      const users = getAllUsers()

      const pendingOrders = orders.filter(order => order.status === 'Pending')
      const shippedOrders = orders.filter(order => order.status === 'Shipped')
      const deliveredOrders = orders.filter(order => order.status === 'Delivered')
      const cancelledOrders = orders.filter(order => order.status === 'Cancelled')
      const pendingPayments = orders.filter(order => order.payment === 'Unpaid')
      const lowStockProducts = products.filter(product => Number(product.stock || 0) > 0 && Number(product.stock || 0) <= 10)
      const outOfStockProducts = products.filter(product => Number(product.stock || 0) <= 0)

      const totalRevenue = orders.reduce((sum, order) => sum + (Number(order.total) || 0), 0)
      const paidRevenue = orders
        .filter(order => order.payment === 'Paid')
        .reduce((sum, order) => sum + (Number(order.total) || 0), 0)
      const pendingAmount = pendingPayments.reduce((sum, order) => sum + (Number(order.total) || 0), 0)

      return {
        users,
        products,
        orders,
        pendingOrders,
        shippedOrders,
        deliveredOrders,
        cancelledOrders,
        pendingPayments,
        lowStockProducts,
        outOfStockProducts,
        totalRevenue,
        paidRevenue,
        pendingAmount
      }
    }

    const getRecentOrderSnippet = (orders) => {
      if (!orders.length) {
        return 'No matching orders found.'
      }
      const preview = orders.slice(0, 3).map(order => `${order.id} (${order.status}, ${toCurrency(order.total || 0)})`)
      return `Top orders: ${preview.join(', ')}`
    }

    const generateReply = (input) => {
      const normalized = input.toLowerCase()
      const m = buildLiveMetrics()

      if (
        normalized.includes('snapshot') ||
        normalized.includes('kpi') ||
        normalized.includes('summary') ||
        normalized.includes('everything')
      ) {
        return [
          `Live Snapshot: ${m.orders.length} total orders (${m.pendingOrders.length} pending, ${m.shippedOrders.length} shipped, ${m.deliveredOrders.length} delivered, ${m.cancelledOrders.length} cancelled).`,
          `Payments: ${m.pendingPayments.length} unpaid orders worth ${toCurrency(m.pendingAmount)}. Paid revenue is ${toCurrency(m.paidRevenue)} of total ${toCurrency(m.totalRevenue)}.`,
          `Inventory: ${m.products.length} products, ${m.lowStockProducts.length} low stock, ${m.outOfStockProducts.length} out of stock.`,
          `Users: ${m.users.length} registered users.`
        ].join(' ')
      }

      if (normalized.includes('user')) {
        return `There are ${m.users.length} registered users. Admin user management can view and delete non-protected accounts.`
      }

      if (normalized.includes('pending order') || normalized.includes('orders pending')) {
        return `${m.pendingOrders.length} pending orders right now. ${getRecentOrderSnippet(m.pendingOrders)}`
      }

      if (normalized.includes('delivered')) {
        return `${m.deliveredOrders.length} delivered orders. ${getRecentOrderSnippet(m.deliveredOrders)}`
      }

      if (normalized.includes('order')) {
        return `Orders now: ${m.orders.length} total (${m.pendingOrders.length} pending, ${m.shippedOrders.length} shipped, ${m.deliveredOrders.length} delivered, ${m.cancelledOrders.length} cancelled). ${getRecentOrderSnippet(m.orders)}`
      }

      if (normalized.includes('low stock')) {
        const topLowStock = m.lowStockProducts.slice(0, 3).map(product => `${product.name} (${product.stock})`)
        return `${m.lowStockProducts.length} low stock products. ${topLowStock.length ? `Top low stock: ${topLowStock.join(', ')}.` : ''}`.trim()
      }

      if (normalized.includes('out of stock')) {
        const topOutOfStock = m.outOfStockProducts.slice(0, 3).map(product => product.name)
        return `${m.outOfStockProducts.length} products are out of stock. ${topOutOfStock.length ? `Examples: ${topOutOfStock.join(', ')}.` : ''}`.trim()
      }

      if (normalized.includes('inventory') || normalized.includes('stock')) {
        return `Inventory status: ${m.products.length} products, ${m.lowStockProducts.length} low stock, ${m.outOfStockProducts.length} out of stock.`
      }

      if (normalized.includes('pending payment') || normalized.includes('unpaid')) {
        return `${m.pendingPayments.length} unpaid orders totaling ${toCurrency(m.pendingAmount)}.`
      }

      if (normalized.includes('payment')) {
        return `Payments summary: ${m.pendingPayments.length} unpaid orders worth ${toCurrency(m.pendingAmount)}. Paid revenue is ${toCurrency(m.paidRevenue)}.`
      }

      if (normalized.includes('revenue') || normalized.includes('sales')) {
        return `Revenue now: total ${toCurrency(m.totalRevenue)}, paid ${toCurrency(m.paidRevenue)}, pending ${toCurrency(m.pendingAmount)}.`
      }

      if (normalized.includes('dashboard')) {
        return `You are on ${currentRouteLabel.value}. Live numbers: ${m.orders.length} orders, ${m.pendingPayments.length} unpaid orders, ${m.products.length} products.`
      }

      if (normalized.includes('help') || normalized.includes('what can')) {
        return 'Ask for: live KPI snapshot, pending orders, pending payments amount, delivered orders, low stock products, out-of-stock products, users count, or revenue.'
      }

      return `Current quick stats: ${m.pendingOrders.length} pending orders, ${m.pendingPayments.length} unpaid orders (${toCurrency(m.pendingAmount)}), ${m.lowStockProducts.length} low stock products.`
    }

    const handleSubmit = async () => {
      const trimmed = draft.value.trim()
      if (!trimmed) {
        return
      }

      await addMessage('user', trimmed)
      draft.value = ''
      await addMessage('assistant', generateReply(trimmed))
    }

    const sendPrompt = async (prompt) => {
      draft.value = prompt
      await handleSubmit()
    }

    return {
      isOpen,
      draft,
      messagesPane,
      messages,
      roleLabel,
      currentRouteLabel,
      promptList,
      sendPrompt,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.assistant-shell {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1300;
}

.assistant-launcher {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(180, 140, 40, 0.98), rgba(110, 159, 58, 0.95));
  color: #121212;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35);
}

.assistant-launcher-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.24);
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.assistant-panel {
  width: min(380px, calc(100vw - 32px));
  max-height: min(620px, calc(100vh - 32px));
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(18, 22, 18, 0.98), rgba(12, 15, 12, 0.96));
  border: 1px solid rgba(180, 140, 40, 0.2);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(18px);
}

.assistant-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.assistant-eyebrow {
  margin: 0 0 4px;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.55);
}

.assistant-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.assistant-close {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
  font-size: 1.35rem;
  cursor: pointer;
}

.assistant-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.assistant-summary span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.assistant-messages {
  min-height: 180px;
  max-height: 250px;
  overflow: auto;
  display: grid;
  gap: 10px;
  padding-right: 4px;
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 90%;
  padding: 12px 14px;
  border-radius: 16px;
  line-height: 1.45;
  font-size: 0.92rem;
}

.message-row.user .bubble {
  background: linear-gradient(135deg, rgba(180, 140, 40, 0.95), rgba(110, 159, 58, 0.95));
  color: #121212;
  border-bottom-right-radius: 6px;
}

.message-row.assistant .bubble {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom-left-radius: 6px;
}

.assistant-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.prompt-chip {
  border: 1px solid rgba(180, 140, 40, 0.2);
  background: rgba(180, 140, 40, 0.08);
  color: var(--text-primary);
  padding: 8px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
}

.assistant-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.assistant-form input {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  padding: 12px 14px;
  outline: none;
}

.assistant-form button {
  border: none;
  border-radius: 14px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #b48c28, #6e9f3a);
  color: #111;
  font-weight: 700;
  cursor: pointer;
}

:global(body.light) .assistant-panel {
  background: rgba(255, 255, 255, 0.96);
  border-color: rgba(0, 0, 0, 0.1);
}

:global(body.light) .assistant-close,
:global(body.light) .assistant-summary span,
:global(body.light) .prompt-chip,
:global(body.light) .assistant-form input {
  background: rgba(0, 0, 0, 0.04);
  color: #1a1a1a;
}

:global(body.light) .message-row.assistant .bubble {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.08);
  color: #1a1a1a;
}

@media (max-width: 640px) {
  .assistant-shell {
    right: 16px;
    left: 16px;
    bottom: 16px;
  }

  .assistant-panel {
    width: 100%;
  }

  .assistant-form {
    grid-template-columns: 1fr;
  }
}
</style>