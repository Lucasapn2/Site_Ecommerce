   // Variáveis globais para armazenar os detalhes do produto selecionado
    var selectedProduct = null;
    var cartItems = [];


  // Função para exibir o formulário de compra ao clicar em "Comprar"
  function buyProduct(productId, productName, productImage, productPrice) {


    // Exibe o modal de compra
    $('#purchaseModal').modal('show');

   // Armazena os detalhes do produto selecionado em uma variável global
    selectedProduct = {
      id: productId,
      name: productName,
      image: productImage,
      price: parseFloat(productPrice)
    };

      // Exibe o modal de compra
      $('#purchaseModal').modal('show');
      document.getElementById("productName").value = productName;
      document.getElementById("productImage").value = productImage;
      document.getElementById("productPrice").value = productPrice;
    }

    // Função para concluir a compra ao clicar em "Concluir"
    function concludePurchase() {
      var customerName = document.getElementById("customerName").value;
      var customerEmail = document.getElementById("customerEmail").value;
      // Aqui você pode adicionar a lógica para coletar outras informações do usuário
      // como telefone e localidade, se necessário.



      // Constrói o link do WhatsApp com as informações do usuário preenchidas
      var message = `Olá, meu nome é ${customerName}, estou interessado em comprar o produto: ${selectedProduct.name}, no valor de R$ ${selectedProduct.price.toFixed(2)}.`;
      var whatsappLink = `https://api.whatsapp.com/send?phone=SEU_NÚMERO_DE_TELEFONE&text=${encodeURIComponent(message)}`;

      // Abre o link do WhatsApp no mesmo navegador
      window.open(whatsappLink, '_blank');

      // Limpa os campos do formulário
      document.getElementById("customerName").value = "";
      document.getElementById("customerEmail").value = "";

      // Esconde o modal após a finalização da compra
      $('#purchaseModal').modal('hide');

      // Exibe o modal de sucesso após a compra
      $('#successModal').modal('show');

      // Mensagem de sucesso (opcional)
      // alert("Compra realizada com sucesso! Obrigado, " + customerName + "!");
    }

    // Função para cancelar a compra e limpar os campos do formulário
    function cancelPurchase() {
      document.getElementById("customerName").value = "";
      document.getElementById("customerEmail").value = "";
      $('#purchaseModal').modal('hide');
    }

    // Função para adicionar um produto ao carrinho
    function addToCart(productId, productName, productImage, productPrice) {
      // Lógica para adicionar o produto ao carrinho
      var item = {
        id: productId,
        name: productName,
        image: productImage,
        price: parseFloat(productPrice)
      };
      cartItems.push(item);

      var cartItemsDiv = document.getElementById("cartItems");
      var cartItem = document.createElement("div");
      cartItem.className = "cart-item";
      cartItem.innerHTML = `
        <img src="${productImage}" alt="${productName}" style="width: 420px; height: 420px; object-fit: cover;">
        <div style="flex-grow: 1;">
          <p class="cart-item-name" style="font-weight: bold; color: #000;">${productName}</p>
          <p class="card-text card-price">Preço: R$ ${productPrice}</p>
        </div>
        <button class="btn btn-danger" onclick="removeFromCart(${cartItems.length - 1})">Remover</button>
      `;
      cartItemsDiv.appendChild(cartItem);

      updateCartTotal();
      alert(`Produto "${productName}" adicionado ao carrinho!`);

      // Role a página para o carrinho de compras após adicionar o item
      document.getElementById("cartContent").scrollIntoView({ behavior: "smooth" });
    }

    // Função para remover um produto do carrinho
    function removeFromCart(index) {
      cartItems.splice(index, 1);
      var cartItemsDiv = document.getElementById("cartItems");
      cartItemsDiv.removeChild(cartItemsDiv.childNodes[index]);

      updateCartTotal();
    }

    // Função para atualizar o total do carrinho
    function updateCartTotal() {
      var cartTotal = 0;
      for (var i = 0; i < cartItems.length; i++) {
        cartTotal += parseFloat(cartItems[i].price);
      }
      document.getElementById("cartTotalValue").textContent = cartTotal.toFixed(2);
      document.getElementById("cartEmptyMessage").style.display = cartItems.length === 0 ? "block" : "none";
    }

    // Função para finalizar a compra
    function finalizePurchase() {
      if (cartItems.length === 0) {
        alert("Seu carrinho está vazio. Adicione itens antes de finalizar a compra.");
      } else {
        // Redirecionar para o formulário de compra com as informações necessárias
        window.location.href = `/formulario-compra?total=${document.getElementById("cartTotalValue").textContent}`;
      }
    }

    // Função para limpar o carrinho
    function clearCart() {
      cartItems = [];
      var cartItemsDiv = document.getElementById("cartItems");
      while (cartItemsDiv.firstChild) {
        cartItemsDiv.removeChild(cartItemsDiv.firstChild);
      }

      updateCartTotal();
    }

    $(document).ready(function () {
      $('.carousel-wrapper').slick({
        dots: true,
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
        prevArrow: '<button type="button" class="slick-prev"><i class="bi bi-arrow-left"></i></button>',
        nextArrow: '<button type="button" class="slick-next"><i class="bi bi-arrow-right"></i></button>'
      });
    });

