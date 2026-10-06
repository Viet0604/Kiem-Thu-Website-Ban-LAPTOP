/**
 * LAPTOP STORE - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

    // ===== Flash Message Auto-dismiss =====
    const flashMsg = document.querySelector('.flash-container .alert');
    if (flashMsg) {
        setTimeout(() => {
            flashMsg.style.transition = 'opacity 0.5s, transform 0.5s';
            flashMsg.style.opacity = '0';
            flashMsg.style.transform = 'translateX(50px)';
            setTimeout(() => flashMsg.parentElement?.remove(), 500);
        }, 4000);
    }

    // ===== Cart Quantity Controls =====
    document.querySelectorAll('.btn-qty-minus').forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.closest('.quantity-control').querySelector('.qty-input');
            let val = parseInt(input.value) || 1;
            if (val > 1) {
                input.value = val - 1;
                this.closest('form')?.submit();
            }
        });
    });

    document.querySelectorAll('.btn-qty-plus').forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.closest('.quantity-control').querySelector('.qty-input');
            let val = parseInt(input.value) || 1;
            const max = parseInt(input.getAttribute('max')) || 99;
            if (val < max) {
                input.value = val + 1;
                this.closest('form')?.submit();
            }
        });
    });

    // ===== Add to Cart Animation =====
    document.querySelectorAll('.btn-add-cart').forEach(btn => {
        btn.addEventListener('click', function (e) {
            // Add pulse animation
            this.style.transform = 'scale(0.85)';
            setTimeout(() => {
                this.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }, 150);
        });
    });

    // ===== Confirm Delete Actions =====
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function (e) {
            const msg = this.getAttribute('data-confirm') || 'Bạn có chắc chắn?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // ===== Admin Sidebar Toggle (Mobile) =====
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', function () {
            adminSidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 991 && adminSidebar.classList.contains('show')) {
                if (!adminSidebar.contains(e.target) && e.target !== sidebarToggle) {
                    adminSidebar.classList.remove('show');
                }
            }
        });
    }

    // ===== Image Preview for Product Upload =====
    const imageInput = document.getElementById('productImage');
    const imagePreview = document.getElementById('imagePreview');
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ===== Form Validation Feedback =====
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // ===== Smooth scroll for anchor links =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ===== Price range display =====
    const priceRange = document.getElementById('priceRange');
    const priceDisplay = document.getElementById('priceDisplay');
    if (priceRange && priceDisplay) {
        priceRange.addEventListener('input', function () {
            const val = parseInt(this.value);
            priceDisplay.textContent = new Intl.NumberFormat('vi-VN').format(val) + ' ₫';
        });
    }

    // ===== Search input auto-submit with debounce =====
    let searchTimeout;
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.closest('form')?.submit();
            }, 800);
        });
    }

});
