<template>
  <footer class="footer">
    <div class="footer-content">
      <p>&copy; 2026 YUMSIE Wholesale Distribution System. All rights reserved.</p>
      <div class="footer-links">
        <a href="#" class="footer-link">Privacy Policy</a>
        <a href="#" class="footer-link">Terms of Service</a>
        <a href="#" class="footer-link">Contact</a>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>


<style scoped>
.footer {
  margin-top: auto;
  padding: 24px 40px;

  background: linear-gradient(
    145deg,
    rgba(18, 22, 18, 0.95),
    rgba(14, 18, 14, 0.95)
  );

  backdrop-filter: blur(10px);

  border-top: 1px solid rgba(170, 140, 60, 0.25);

  box-shadow:
    0 -5px 20px rgba(0, 0, 0, 0.4),
    0 0 10px rgba(170, 140, 60, 0.05);

  color: #cfcfcf;
}

/* Layout */
.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;

  max-width: 1400px;
  margin: 0 auto;
  font-size: 0.9rem;
}

/* Left text */
.footer-content p {
  margin: 0;
  letter-spacing: 0.5px;
}

/* Links */
.footer-links {
  display: flex;
  gap: 28px;
}

/* Individual link */
.footer-link {
  position: relative;
  text-decoration: none;
  font-size: 0.85rem;
  letter-spacing: 0.5px;

  color: #bfbfbf;
  transition: all 0.3s ease;
}

/* Underline animation */
.footer-link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 0%;
  height: 2px;

  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  transition: width 0.3s ease;
}

.footer-link:hover {
  color: #ffffff;
}

.footer-link:hover::after {
  width: 100%;
}

/* Mobile */
@media (max-width: 900px) {
  .footer-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .footer-links {
    gap: 18px;
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>