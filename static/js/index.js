class OrderManager {
    constructor() {
        this.currentOrder = {
            client: null,
            items: [],
            shipping: 0,
            total: 0
        };
    }

    init() {
        // Eventos del primer formulario
        document.querySelector('.submit-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.saveClientData();
            this.showProductsPanel();
        });

        // Eventos del panel de productos
        document.querySelector('.back-btn').addEventListener('click', () => {
            this.showCustomerForm();
        });

        document.querySelector('.payment-btn').addEventListener('click', () => {
            this.processPayment();
        });
    }

    saveClientData() {
        this.currentOrder.client = {
            name: document.querySelector('input[type="text"]').value,
            phone: document.querySelector('input[type="tel"]').value,
            address: document.querySelector('input[placeholder="Calle"]').value
        };

        // Actualizar resumen del cliente
        document.getElementById('client-name').textContent = this.currentOrder.client.name;
        document.getElementById('client-phone').textContent = this.currentOrder.client.phone;
    }

    showProductsPanel() {
        document.getElementById('customer-form').style.display = 'none';
        document.getElementById('products-panel').style.display = 'block';
        this.loadProducts();
    }

    showCustomerForm() {
        document.getElementById('products-panel').style.display = 'none';
        document.getElementById('customer-form').style.display = 'block';
    }

    loadProducts() {
        // Aquí deberías hacer una llamada AJAX para cargar los productos
        fetch('/api/products')
            .then(response => response.json())
            .then(data => this.renderProducts(data));
    }

    renderProducts(products) {
        const productsContainer = document.querySelector('.products-list');
        productsContainer.innerHTML = products.map(product => `
            <div class="product-card" data-id="${product.id}">
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p>$${product.price}</p>
                <button onclick="orderManager.addProduct(${JSON.stringify(product)})">
                    Agregar
                </button>
            </div>
        `).join('');
    }

    addProduct(product) {
        const existingItem = this.currentOrder.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.currentOrder.items.push({
                ...product,
                quantity: 1
            });
        }

        this.updateOrderSummary();
    }

    updateOrderSummary() {
        const selectedProducts = document.querySelector('.selected-products');
        selectedProducts.innerHTML = this.currentOrder.items.map(item => `
            <div class="order-item">
                <span>${item.name}</span>
                <span>x${item.quantity}</span>
                <span>$${item.price * item.quantity}</span>
                <button onclick="orderManager.removeProduct(${item.id})">Eliminar</button>
            </div>
        `).join('');

        this.calculateTotals();
    }

    calculateTotals() {
        const subtotal = this.currentOrder.items.reduce(
            (sum, item) => sum + (item.price * item.quantity), 0
        );
        
        document.getElementById('subtotal').textContent = subtotal;
        document.getElementById('shipping').textContent = this.currentOrder.shipping;
        document.getElementById('total').textContent = subtotal + this.currentOrder.shipping;
    }

    processPayment() {
        // Aquí implementarías la lógica de pago
        console.log('Procesando pago:', this.currentOrder);
    }
}

// Inicializar
const orderManager = new OrderManager();
document.addEventListener('DOMContentLoaded', () => orderManager.init());


