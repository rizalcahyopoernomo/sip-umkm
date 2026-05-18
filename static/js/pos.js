/**
 * POS SYSTEM CORE LOGIC - STABILIZED VERSION
 * Project: SIP-UMKM Retail
 */

// =========================
// 1. GLOBAL STATE
// =========================
let cart = [];

let holdCart = null;

let isProcessingCheckout = false;


// =========================
// 2. AUDIO
// =========================
const soundAdd = new Audio(
    'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'
);

const soundSuccess = new Audio(
    'https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3'
);


// =========================
// 3. INITIALIZATION
// =========================
document.addEventListener(
    'DOMContentLoaded',
    function () {

        startLiveClock();

        setupEventListeners();

        renderCart();
    }
);


// =========================
// 4. LIVE CLOCK
// =========================
function startLiveClock() {

    const clockElement =
        document.getElementById('clock');

    const dateElement =
        document.getElementById('current-date');

    const dateOptions = {

        weekday: 'long',

        year: 'numeric',

        month: 'long',

        day: 'numeric'
    };

    function updateDateTime() {

        const now = new Date();

        if (dateElement) {

            dateElement.innerText =
                now.toLocaleDateString(
                    'id-ID',
                    dateOptions
                );
        }

        if (clockElement) {

            clockElement.innerText =
                now.toLocaleTimeString(
                    'id-ID',
                    {

                        hour12: false,

                        hour: '2-digit',

                        minute: '2-digit',

                        second: '2-digit'

                    }

                ).replace(/:/g, '.');
        }
    }

    updateDateTime();

    setInterval(updateDateTime, 1000);
}


// =========================
// 5. EVENT LISTENER
// =========================
function setupEventListeners() {

    // =========================
    // SEARCH SHORTCUT
    // =========================
    document.addEventListener(
        'keydown',
        function (e) {

            if (e.key === '/') {

                e.preventDefault();

                document
                    .getElementById('productSearch')
                    ?.focus();
            }
        }
    );

    // =========================
    // PRODUCT SEARCH
    // =========================
    document
        .getElementById('productSearch')
        ?.addEventListener(
            'input',
            function (e) {

                const value =
                    e.target.value.toLowerCase();

                document
                    .querySelectorAll('.product-item')
                    .forEach(item => {

                        const name =
                            item.getAttribute('data-name');

                        item.style.display =
                            name.includes(value)
                                ? 'block'
                                : 'none';
                    });
            }
        );

    // =========================
    // DISCOUNT
    // =========================
    document
        .getElementById('discountInput')
        ?.addEventListener(
            'input',
            calculateTotal
        );

    // =========================
    // PAYMENT INPUT
    // =========================
    const paidInput =
        document.getElementById('paidAmount');

    if (paidInput) {

        paidInput.addEventListener(
            'input',
            calculateChange
        );

        paidInput.addEventListener(
            'keydown',
            function (e) {

                const allowedKeys = [

                    'Backspace',
                    'Tab',
                    'Enter',
                    'ArrowLeft',
                    'ArrowRight',
                    'Delete',
                    'Escape'
                ];

                const isNumber =
                    e.key >= '0' &&
                    e.key <= '9';

                if (
                    !isNumber &&
                    !allowedKeys.includes(e.key)
                ) {

                    e.preventDefault();
                }
            }
        );

        paidInput.addEventListener(
            'paste',
            function (e) {

                const pasteData = (
                    e.clipboardData ||
                    window.clipboardData
                ).getData('text');

                if (!/^\d+$/.test(pasteData)) {

                    e.preventDefault();
                }
            }
        );
    }

    // =========================
    // QUICK CASH
    // =========================
    document
        .querySelectorAll('.quick-cash')
        .forEach(btn => {

            btn.addEventListener(
                'click',
                function () {

                    const amount =
                        parseInt(
                            this.getAttribute('data-val')
                        );

                    paidInput.value = amount;

                    calculateChange();

                    soundAdd.play();
                }
            );
        });

    // =========================
    // CATEGORY FILTER
    // =========================
    document
        .querySelectorAll('.filter-btn')
        .forEach(btn => {

            btn.addEventListener(
                'click',
                function () {

                    document
                        .querySelectorAll('.filter-btn')
                        .forEach(b => {

                            b.classList.remove(
                                'active',
                                'btn-primary'
                            );
                        });

                    this.classList.add(
                        'active',
                        'btn-primary'
                    );

                    const category =
                        this.getAttribute(
                            'data-category'
                        );

                    document
                        .querySelectorAll('.product-item')
                        .forEach(item => {

                            const itemCategory =
                                item.getAttribute(
                                    'data-category'
                                );

                            item.style.display =
                                (
                                    category === 'all' ||
                                    itemCategory === category
                                )
                                    ? 'block'
                                    : 'none';
                        });
                }
            );
        });
}


// =========================
// 6. ADD TO CART
// =========================
function handleAddToCart(element) {

    const id =
        element.getAttribute('data-id');

    const name =
        element.getAttribute('data-name');

    const price =
        parseFloat(
            element.getAttribute('data-price')
        );

    const stock =
        parseInt(
            element.getAttribute('data-stock')
        );

    addToCart(
        id,
        name,
        price,
        stock
    );
}


function addToCart(id, name, price, stock) {

    const existing =
        cart.find(item => item.id === id);

    if (existing) {

        if (existing.qty < stock) {

            existing.qty++;

            soundAdd.play();

            showToast(
                `Jumlah ${name} ditambah`,
                'success'
            );

        } else {

            showToast(
                "Stok tidak mencukupi!",
                "danger"
            );
        }

    } else {

        cart.push({

            id,
            name,
            price,
            qty: 1,
            stock
        });

        soundAdd.play();

        showToast(
            `${name} masuk keranjang`,
            'success'
        );
    }

    renderCart();
}


// =========================
// 7. UPDATE QTY
// =========================
function updateQty(id, delta) {

    const item =
        cart.find(i => i.id === id);

    if (!item) return;

    if (
        item.qty + delta > 0 &&
        item.qty + delta <= item.stock
    ) {

        item.qty += delta;

    } else if (item.qty + delta <= 0) {

        removeFromCart(id);

    } else {

        showToast(
            "Stok tidak mencukupi!",
            "danger"
        );
    }

    renderCart();
}


// =========================
// 8. REMOVE CART
// =========================
function removeFromCart(id) {

    cart =
        cart.filter(i => i.id !== id);

    renderCart();
}


// =========================
// 9. RENDER CART
// =========================
function renderCart() {

    const container =
        document.getElementById('cartItems');

    const emptyMsg =
        document.getElementById('emptyCart');

    const countBadge =
        document.getElementById('cartCount');

    const btnCheckout =
        document.getElementById('btnCheckout');

    if (!container) return;

    container.innerHTML = '';

    let subtotal = 0;

    // =========================
    // EMPTY CART
    // =========================
    if (cart.length === 0) {

        if (emptyMsg) {

            emptyMsg.style.display = 'block';
        }

        if (btnCheckout) {

            btnCheckout.disabled = true;
        }

    } else {

        if (emptyMsg) {

            emptyMsg.style.display = 'none';
        }

        cart.forEach(item => {

            const itemTotal =
                item.price * item.qty;

            subtotal += itemTotal;

            const div =
                document.createElement('div');

            div.className =
                'cart-item d-flex justify-content-between align-items-center animate__animated animate__fadeInUp';

            div.innerHTML = `

                <div class="flex-grow-1">

                    <h6 class="m-0 small fw-bold text-dark">
                        ${item.name}
                    </h6>

                    <small class="text-muted">
                        Rp ${item.price.toLocaleString('id-ID')} / pcs
                    </small>

                </div>

                <div class="d-flex align-items-center gap-2">

                    <div class="input-group input-group-sm"
                         style="width:100px;">

                        <button
                            class="btn btn-light border"
                            onclick="updateQty('${item.id}', -1)">

                            -

                        </button>

                        <span class="form-control text-center bg-white border-0 small fw-bold">

                            ${item.qty}

                        </span>

                        <button
                            class="btn btn-light border"
                            onclick="updateQty('${item.id}', 1)">

                            +

                        </button>

                    </div>

                    <span
                        class="small fw-bold text-primary ms-2"
                        style="min-width:80px;text-align:right;">

                        Rp ${itemTotal.toLocaleString('id-ID')}

                    </span>

                    <button
                        class="btn btn-link text-danger p-0 ms-2"
                        onclick="removeFromCart('${item.id}')">

                        <i class="fas fa-times-circle"></i>

                    </button>

                </div>
            `;

            container.appendChild(div);
        });
    }

    if (countBadge) {

        countBadge.innerText =
            `${cart.length} Items`;
    }

    document.getElementById('subtotal').innerText =
        'Rp ' +
        subtotal.toLocaleString('id-ID');

    calculateTotal();
}


// =========================
// 10. CALCULATE TOTAL
// =========================
function calculateTotal() {

    const subtotal =
        parseInt(
            document
                .getElementById('subtotal')
                .innerText
                .replace(/[^\d]/g, '')
        ) || 0;

    const discount =
        parseInt(
            document
                .getElementById('discountInput')
                .value
        ) || 0;

    const total =
        Math.max(0, subtotal - discount);

    document.getElementById('totalPrice').innerText =
        'Rp ' +
        total.toLocaleString('id-ID');

    calculateChange();
}


// =========================
// 11. CALCULATE CHANGE
// =========================
function calculateChange() {

    const total =
        parseInt(
            document
                .getElementById('totalPrice')
                .innerText
                .replace(/[^\d]/g, '')
        ) || 0;

    const paid =
        parseInt(
            document
                .getElementById('paidAmount')
                .value
        ) || 0;

    const change = paid - total;

    const changeDisplay =
        document.getElementById('changeAmount');

    const btnCheckout =
        document.getElementById('btnCheckout');

    // =========================
    // VALID PAYMENT
    // =========================
    if (
        paid > 0 &&
        change >= 0 &&
        cart.length > 0
    ) {

        changeDisplay.innerText =
            'Rp ' +
            change.toLocaleString('id-ID');

        changeDisplay.className =
            'fw-bold m-0 text-success';

        btnCheckout.disabled = false;

    }

    // =========================
    // INVALID PAYMENT
    // =========================
    else if (
        paid > 0 &&
        change < 0
    ) {

        changeDisplay.innerText =
            'Kurang: Rp ' +
            Math.abs(change)
                .toLocaleString('id-ID');

        changeDisplay.className =
            'fw-bold m-0 text-danger';

        btnCheckout.disabled = true;

    }

    // =========================
    // DEFAULT
    // =========================
    else {

        changeDisplay.innerText = 'Rp 0';

        changeDisplay.className =
            'fw-bold m-0 text-muted';

        btnCheckout.disabled = true;
    }
}


// =========================
// 12. PROCESS CHECKOUT
// =========================
async function processCheckout() {

    // =========================
    // PREVENT DOUBLE CLICK
    // =========================
    if (isProcessingCheckout) {

        return;
    }

    if (cart.length === 0) {

        showToast(
            "Keranjang masih kosong!",
            "danger"
        );

        return;
    }

    const totalValue =
        parseInt(
            document
                .getElementById('totalPrice')
                .innerText
                .replace(/[^\d]/g, '')
        ) || 0;

    const paidValue =
        parseInt(
            document
                .getElementById('paidAmount')
                .value
        ) || 0;

    // =========================
    // VALIDASI PEMBAYARAN
    // =========================
    if (paidValue < totalValue) {

        showToast(
            "Uang pembayaran tidak cukup!",
            "danger"
        );

        return;
    }

    // =========================
    // LOCK CHECKOUT
    // =========================
    isProcessingCheckout = true;

    const btn =
        document.getElementById('btnCheckout');

    const originalHTML =
        btn.innerHTML;

    // =========================
    // LOADING BUTTON
    // =========================
    btn.disabled = true;

    btn.style.opacity = '0.7';

    btn.style.cursor = 'wait';

    btn.innerHTML = `

        <span
            class="spinner-border spinner-border-sm me-2">
        </span>

        Memproses...

    `;

    // =========================
    // BUILD PAYLOAD
    // =========================
    const payload = {

        customer:
            document
                .getElementById('customerName')
                ?.value ||
            "Pelanggan Umum",

        subtotal:
            parseInt(
                document
                    .getElementById('subtotal')
                    .innerText
                    .replace(/[^\d]/g, '')
            ) || 0,

        discount:
            parseInt(
                document
                    .getElementById('discountInput')
                    .value
            ) || 0,

        total: totalValue,

        payment_method:
            document
                .getElementById('payQRIS')
                ?.checked
                    ? 'QRIS'
                    : 'Tunai',

        amount_paid: paidValue,

        change:
            paidValue - totalValue,

        items:
            cart.map(item => ({

                id: item.id,

                name: item.name,

                price: item.price,

                qty: item.qty
            }))
    };

    try {

        // =========================
        // FETCH CHECKOUT
        // =========================
        const response = await fetch(
            '/cashier/checkout',
            {

                method: 'POST',

                headers: {

                    'Content-Type':
                        'application/json'
                },

                body:
                    JSON.stringify(payload)
            }
        );

        // =========================
        // VALIDASI RESPONSE
        // =========================
        if (!response.ok) {

            throw new Error(
                'Server gagal memproses transaksi'
            );
        }

        const result =
            await response.json();

        // =========================
        // SUCCESS
        // =========================
        if (result.success) {

            soundSuccess.play();

            showToast(
                "Transaksi berhasil!",
                "success"
            );

            btn.innerHTML = `

                <i class="fas fa-check-double me-2"></i>

                BERHASIL

            `;

            btn.className =
                "btn btn-success w-100 py-3 rounded-4 fw-bold shadow";

            localStorage.removeItem('cart');

            cart = [];

            renderCart();

            setTimeout(() => {

                window.location.href =
                    result.redirect_url;

            }, 1000);
        }

        // =========================
        // FAILED
        // =========================
        else {

            throw new Error(
                result.message ||
                'Checkout gagal'
            );
        }

    } catch (error) {

        showToast(
            error.message ||
            "Terjadi kesalahan server",
            "danger"
        );

        btn.disabled = false;

        btn.style.opacity = '1';

        btn.style.cursor = 'pointer';

        btn.innerHTML = originalHTML;

    } finally {

        isProcessingCheckout = false;
    }
}


// =========================
// 13. TOAST
// =========================
function showToast(
    message,
    type = 'success'
) {

    const toastContainer =
        document.querySelector(
            '.toast-container'
        );

    if (!toastContainer) return;

    const div =
        document.createElement('div');

    div.className =
        `custom-alert alert-${type} shadow-lg`;

    div.style.minWidth = "250px";

    div.innerHTML = `

        <div class="alert-icon">

            <i class="fas ${
                type === 'danger'
                ? 'fa-exclamation-circle'
                : 'fa-check-circle'
            }"></i>

        </div>

        <div class="alert-message fw-bold">

            ${message}

        </div>
    `;

    toastContainer.appendChild(div);

    setTimeout(() => {

        div.style.animation =
            "slideDown 0.5s ease-in reverse";

        setTimeout(
            () => div.remove(),
            500
        );

    }, 3000);
}


// =========================
// 14. HOLD ORDER
// =========================
function holdOrder() {

    if (cart.length > 0) {

        holdCart =
            JSON.parse(
                JSON.stringify(cart)
            );

        cart = [];

        renderCart();

        showToast(
            "Pesanan berhasil ditahan!",
            "info"
        );
    }
}