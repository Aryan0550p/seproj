# YUMSIE Wholesale Distribution System

A modern Vue 3 frontend application for managing wholesale distribution operations including inventory, orders, payments, delivery, and reporting.

## Features

- **Admin Dashboard**: Overview of key metrics and recent activity for administrators
- **Salesman Dashboard**: Performance tracking and order management for sales staff
- **Retailer Dashboard**: Personalized catalog browsing and order history for B2B customers
- **Inventory Management**: Track stock levels, product information, and alerts
- **Order Management**: Process and track customer orders across different user roles
- **Payment Management**: Handle payments, invoices, and financial tracking
- **Customer Management**: Detailed customer profiles and performance analytics
- **Reports & Analytics**: Comprehensive business insights and performance reporting

## Tech Stack

- **Frontend**: Vue 3, Vue Router
- **State Management**: Simple reactive store (`store.js`)
- **Authentication**: Local-storage based auth system (`auth.js`)
- **Styling**: Vanilla CSS3 with a clean, modern design system
- **Build Tool**: Vite

## Project Structure

```
src/
├── assets/
│   └── styles.css          # Global styles and design system
├── components/
│   ├── Navbar.vue          # Dynamic navigation component
│   └── Footer.vue          # Footer component
├── pages/
│   ├── Login.vue           # Secure entry point
│   ├── Dashboard.vue       # Admin overview
│   ├── SalesDashboard.vue  # Sales representative hub
│   ├── RetailerDashboard.vue # B2B customer portal
│   ├── Inventory.vue       # Stock management
│   ├── Orders.vue          # Admin/Global order tracking
│   ├── SalesOrders.vue     # Sales-specific order management
│   ├── Customers.vue       # CRM and customer details
│   ├── Payments.vue        # Financial tracking
│   ├── Delivery.vue        # Logistics and fulfillment
│   ├── Reports.vue         # Business intelligence
│   └── Performance.vue     # Data-driven performance metrics
├── router/
│   └── index.js            # Vue Router configuration
├── store.js                # Centralized state management
├── auth.js                 # Authentication logic
├── App.vue                 # Root application component
└── main.js                 # Application entry point
```

## Getting Started

### Prerequisites

- Node.js (version 18 or higher recommended)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to the URL shown in the terminal (usually `http://localhost:5173`)

### Build for Production

```bash
npm run build
```

## Available Scripts

- `npm run dev` - Start development server with Vite
- `npm start` - Same as `npm run dev`
- `npm run build` - Build the project for production

## Styling

The application uses a cohesive design system featuring:
- **Responsive Layouts**: Optimized for mobile and desktop
- **Theme Support**: Adaptive for different viewing modes
- **Modern UI Components**: Card-based layouts, smooth transitions, and intuitive navigation
- **Glassmorphism**: Subtle effects for a premium feel

## License

© 2026 YUMSIE Wholesale Distribution System. All rights reserved.
