const translations = {
  en: {
    app_title: "E-Commerce App",
    nav_products: "Products",
    nav_cart: "Cart",
    nav_orders: "My Orders",
    nav_admin: "Admin",
    nav_logout: "Logout",
    nav_login: "Login",
    nav_register: "Register",
    language: "Language",
    login_title: "Login",
    register_title: "Register",
    username: "Username",
    password: "Password",
    login_btn: "Login",
    register_btn: "Create Account",
    no_account: "No account?",
    have_account: "Already have an account?",
    products_title: "Products",
    price: "Price",
    stock: "Stock",
    add_to_cart: "Add to Cart",
    cart_title: "Your Cart",
    product: "Product",
    qty: "Qty",
    total: "Total",
    actions: "Actions",
    update: "Update",
    remove: "Remove",
    subtotal: "Subtotal",
    address: "Delivery Address",
    place_order: "Place Order",
    cart_empty: "Your cart is empty.",
    orders_title: "My Orders",
    order: "Order",
    orders_empty: "No orders yet.",
    admin_products: "Admin Product Management",
    add_product: "Add Product",
    manage_products: "Manage Products",
    update_price: "Update Price",
    delete_product: "Delete Product"
  },
  hi: {
    app_title: "ई-कॉमर्स ऐप",
    nav_products: "उत्पाद",
    nav_cart: "कार्ट",
    nav_orders: "मेरे ऑर्डर",
    nav_admin: "एडमिन",
    nav_logout: "लॉगआउट",
    nav_login: "लॉगिन",
    nav_register: "रजिस्टर",
    language: "भाषा",
    login_title: "लॉगिन",
    register_title: "रजिस्टर",
    username: "यूज़रनेम",
    password: "पासवर्ड",
    login_btn: "लॉगिन",
    register_btn: "खाता बनाएं",
    no_account: "खाता नहीं है?",
    have_account: "पहले से खाता है?",
    products_title: "उत्पाद",
    price: "कीमत",
    stock: "स्टॉक",
    add_to_cart: "कार्ट में जोड़ें",
    cart_title: "आपका कार्ट",
    product: "उत्पाद",
    qty: "मात्रा",
    total: "कुल",
    actions: "कार्य",
    update: "अपडेट",
    remove: "हटाएं",
    subtotal: "उप-योग",
    address: "डिलीवरी पता",
    place_order: "ऑर्डर करें",
    cart_empty: "आपका कार्ट खाली है।",
    orders_title: "मेरे ऑर्डर",
    order: "ऑर्डर",
    orders_empty: "अभी तक कोई ऑर्डर नहीं।",
    admin_products: "एडमिन उत्पाद प्रबंधन",
    add_product: "उत्पाद जोड़ें",
    manage_products: "उत्पाद प्रबंधित करें",
    update_price: "कीमत अपडेट करें",
    delete_product: "उत्पाद हटाएं"
  },
  es: {
    app_title: "Aplicación de Comercio",
    nav_products: "Productos",
    nav_cart: "Carrito",
    nav_orders: "Mis Pedidos",
    nav_admin: "Admin",
    nav_logout: "Cerrar sesión",
    nav_login: "Iniciar sesión",
    nav_register: "Registrarse",
    language: "Idioma",
    login_title: "Iniciar sesión",
    register_title: "Registrarse",
    username: "Usuario",
    password: "Contraseña",
    login_btn: "Entrar",
    register_btn: "Crear cuenta",
    no_account: "¿No tienes cuenta?",
    have_account: "¿Ya tienes cuenta?",
    products_title: "Productos",
    price: "Precio",
    stock: "Stock",
    add_to_cart: "Agregar al carrito",
    cart_title: "Tu carrito",
    product: "Producto",
    qty: "Cant.",
    total: "Total",
    actions: "Acciones",
    update: "Actualizar",
    remove: "Eliminar",
    subtotal: "Subtotal",
    address: "Dirección de entrega",
    place_order: "Realizar pedido",
    cart_empty: "Tu carrito está vacío.",
    orders_title: "Mis pedidos",
    order: "Pedido",
    orders_empty: "Aún no hay pedidos.",
    admin_products: "Gestión de Productos Admin",
    add_product: "Agregar producto",
    manage_products: "Administrar productos",
    update_price: "Actualizar precio",
    delete_product: "Eliminar producto"
  }
};

function applyLanguage(lang) {
  const selected = translations[lang] || translations.en;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (selected[key]) {
      el.textContent = selected[key];
    }
  });
}

(function initLanguage() {
  const select = document.getElementById("lang-switch");
  if (!select) {
    return;
  }

  const saved = localStorage.getItem("app_lang") || "en";
  select.value = saved;
  applyLanguage(saved);

  select.addEventListener("change", (event) => {
    const lang = event.target.value;
    localStorage.setItem("app_lang", lang);
    applyLanguage(lang);
  });
})();
