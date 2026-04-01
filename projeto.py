from datetime import datetime

class Produto:
    def __init__(self, id_produto, nome, preco, estoque, loja_nome):
        self.id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self.loja_nome = loja_nome
        
    def is_disponivel(self, quantidade=1):
        return self.estoque >= quantidade
    
    """estoque indisponivel"""    
    def reduzir_estoque(self, quantidade):
        if self.is_disponivel(quantidade):
            self.estoque -= quantidade
            return True
        return False 

    def alterar_preco(self, novo_preco):
        self.preco = novo_preco

    def __str__(self):
        """String representation."""
        status = "Disponível" if self.estoque > 0 else "Indisponível"
        return f"[{self.id_produto}] {self.nome} - R${self.preco:.2f} ({status}: {self.estoque} un.)"
    

    '''Aplicando conceito de herança : Produto Fisico - com peso e com calculo de frete '''
class ProdFisico(Produto):
    def __init__(self, id_produto, nome, preco, estoque, loja_nome, peso_kg):#definindo o que a minha nova classe recebe
        super().__init__(id_produto, nome, preco, estoque, loja_nome) #chamando os conceitos do'mae'
        self.peso_kg = peso_kg #atributo adicionado 
    def calcular_frete(self):
        valor_frete = self.peso_kg * 10.00 #calculo do frete 
        return valor_frete


class ProdDigital(Produto):
    def __init__(self, id_produto, nome, preco, estoque, loja_nome):
        super().__init__(id_produto, nome, preco, estoque, loja_nome)
    def gerar_link(self): 
        nome_url = self.nome.lower().replace(" ", "-")
        link = f"https://newshopee.com.br/arquivos/{self.id_produto}/{nome_url}"
        return f"Arquivo pronto para baixar {link}"

class ItemCarrinho:
    def __init__(self, produto: Produto, quantidade: int):
        self.produto = produto
        self.quantidade = quantidade
        self.preco_adicionado = produto.preco 
        
    def get_subtotal(self):
        return self.preco_adicionado * self.quantidade

class Carrinho:
    def __init__(self):
        self.itens = []
        
    def adicionar(self, produto: Produto, quantidade: int):
        if not produto.is_disponivel(quantidade):
            return f"Erro: Estoque insuficiente para {produto.nome}."
            
        item = ItemCarrinho(produto, quantidade)
        self.itens.append(item)
        return f"{quantidade}x {produto.nome} adicionado ao carrinho por R${produto.preco:.2f} cada."
        
    def remover(self, id_produto):
        for item in self.itens:
            if item.produto.id_produto == id_produto:
                self.itens.remove(item)
                return "Produto removido do carrinho."
        return "Produto não encontrado no carrinho."

    def limpar(self):
        self.itens.clear()

class Pedido:
    def __init__(self, id_pedido, itens, total):
        self.id_pedido = id_pedido
        self.itens = itens
        self.total = total
        self.data = datetime.now()
        self.status = "confirmado"

    def __str__(self):
        return f"Pedido #{self.id_pedido} ({self.data.strftime('%d/%m/%Y %H:%M')}) - Status: {self.status} - Total: R${self.total:.2f}"

class Usuario:
    def __init__(self, id_usuario, nome, email):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.logado = False
        self.carrinho = Carrinho()
        self.historico_pedidos = []
        
    def login(self):
        self.logado = True
        return f"Usuário {self.nome} logado com sucesso."
        
    def logout(self):
        self.logado = False
        return f"Usuário {self.nome} deslogado."
    
'''Aplicando herança em Usuários: Cliente VIP com benefícios'''
class UsuarioVIP(Usuario):
    def __init__(self, id_usuario, nome, email):
        super().__init__(id_usuario, nome, email)
        self.taxa_desconto = 0.10 # VIP tem 10% de desconto

    # Função exclusiva para calcular desconto
    def aplicar_desconto(self, valor_total):
        desconto = valor_total * self.taxa_desconto
        return valor_total - desconto

class Loja:
    def __init__(self, nome_loja, vendedor_nome):
        self.nome_loja = nome_loja
        self.vendedor_nome = vendedor_nome
        self.catalogo = []
        
    def publicar_produto(self, id_produto, nome, preco, estoque):
        produto = Produto(id_produto, nome, preco, estoque, self.nome_loja)
        self.catalogo.append(produto)
        return produto

class Marketplace:
    def __init__(self, nome):
        self.nome = nome
        self.usuarios = {}
        self.lojas = {}
        self.contador_pedidos = 1000
        
    def registrar_usuario(self, id_user, nome, email):
        user = Usuario(id_user, nome, email)
        self.usuarios[id_user] = user
        return user
        
    def criar_loja(self, nome_loja, vendedor_nome):
        loja = Loja(nome_loja, vendedor_nome)
        self.lojas[nome_loja] = loja
        return loja
        
    def buscar_produto(self, termo):
        resultados = []
        for loja in self.lojas.values():
            for produto in loja.catalogo:
                if termo.lower() in produto.nome.lower():
                    resultados.append(produto)
        return resultados
    """Evita compras de produtos sem estoque"""
    def finalizar_compra(self, id_usuario):
        usuario = self.usuarios.get(id_usuario)
        
        if not usuario or not usuario.logado:
            return "Erro: Usuário precisa estar logado para comprar."
            
        if not usuario.carrinho.itens:
            return "Erro: Carrinho vazio."

        total_pedido = 0
        """Atualiza o estoque"""
        for item in usuario.carrinho.itens:
            produto = item.produto
            
            if not produto.is_disponivel(item.quantidade):
                return f"Falha no pedido: O produto '{produto.nome}' está sem estoque suficiente."
                
            """Validação automática de preço"""
            if item.preco_adicionado != produto.preco: 
                return f"DIVERGÊNCIA DE PREÇO: O valor de '{produto.nome}' mudou de R${item.preco_adicionado:.2f} para R${produto.preco:.2f}. Compra bloqueada para evitar prejuízo."
            
            total_pedido += item.get_subtotal()

        for item in usuario.carrinho.itens:
            item.produto.reduzir_estoque(item.quantidade)

        novo_pedido = Pedido(self.contador_pedidos, list(usuario.carrinho.itens), total_pedido)
        usuario.historico_pedidos.append(novo_pedido)
        self.contador_pedidos += 1
        
        usuario.carrinho.limpar()
        
        return f"Sucesso! {novo_pedido}"
    

'''aqui eu adicionei uma main para fazer testes'''

if __name__ == "__main__":
    app = Marketplace("NEW Shopee")
    
    # --- ÁREA DE TESTES (CONFIGURAÇÃO INICIAL) ---
    
    # Criamos o Usuário VIP diretamente para testar a herança
    cliente = UsuarioVIP("U01", "Ricardo VIP", "ricardo.vip@gmail.com")
    app.usuarios[cliente.id_usuario] = cliente 
    cliente.login()
    
    # Criamos a loja e os produtos físicos (comuns)
    loja_padrao = app.criar_loja("NEW Shopee", "Vendedor Ricardo")
    loja_padrao.publicar_produto("1", "Fone Bluetooth", 100.00, 2)
    loja_padrao.publicar_produto("2", "Cabo USB-C", 20.00, 1)

    # Criamos o Produto Digital (Ebook) para testar a herança de produto
    meu_ebook = ProdDigital(id_produto="101", nome="Ebook Projeto Software", preco=45.00, estoque=10000, loja_nome="NewShopee-Digital")
    # Importante: Adicione o ebook ao catálogo para ele aparecer no menu!
    loja_padrao.catalogo.append(meu_ebook)

    # --- PRINTS DE VALIDAÇÃO (O QUE APARECE NO TERMINAL) ---

    print(f"\n--- TESTE DO USUÁRIO VIP (HERANÇA) ---")
    print(f"O usuário {cliente.nome} tem acesso à função de desconto.")
    print(f"Uma compra de R$ 200,00 cai para: R$ {cliente.aplicar_desconto(200.00):.2f}")
    print("--------------------------------------")
    
    print("\n--- TESTE DO PRODUTO DIGITAL (HERANÇA) ---")
    print(f"Produto: {meu_ebook.nome}") 
    print(f"Link Gerado: {meu_ebook.gerar_link()}")
    print("------------------------------------------\n")

    while True:
        print("\n" + "="*45)
        print("=== MENU INTERATIVO DE TESTES (MARKETPLACE) ===")
        print("--- ÁREA DO COMPRADOR ---")
        print("1 - Ver catálogo de produtos")
        print("2 - Adicionar produto ao carrinho")
        print("3 - Ver carrinho")
        print("4 - Simular alteração de preço (Testar trava)")
        print("5 - Finalizar compra")
        print("6 - Ver histórico de pedidos")
        print("\n--- ÁREA DO VENDEDOR ---")
        print("7 - Criar nova loja")
        print("8 - Publicar novo produto em uma loja")
        print("\n0 - Sair do sistema")
        print("="*45)
        
        opcao = input("Escolha uma opção para testar: ")
        
        if opcao == "0":
            print("Encerrando o sistema...")
            break
            
        elif opcao == "1":
            print("\n--- Catálogo Geral ---")
            tem_produto = False
            for loja in app.lojas.values():
                for produto in loja.catalogo:
                    print(f"Loja '{loja.nome_loja}': {produto}")
                    tem_produto = True
            if not tem_produto:
                print("Nenhum produto cadastrado no marketplace.")
                
        elif opcao == "2":
            id_prod = input("Digite o ID do produto: ")
            try:
                qtd = int(input("Digite a quantidade: "))
                # Busca o produto em todas as lojas
                produto_encontrado = None
                for loja in app.lojas.values():
                    for p in loja.catalogo:
                        if p.id_produto == id_prod:
                            produto_encontrado = p
                            break
                
                if produto_encontrado:
                    print(cliente.carrinho.adicionar(produto_encontrado, qtd))
                else:
                    print("Produto não encontrado.")
            except ValueError:
                print("Erro: A quantidade deve ser um número inteiro.")
                
        elif opcao == "3":
            print("\n--- Seu Carrinho ---")
            if not cliente.carrinho.itens:
                print("O carrinho está vazio.")
            else:
                for item in cliente.carrinho.itens:
                    print(f"- {item.quantidade}x {item.produto.nome} (Adicionado por: R${item.preco_adicionado:.2f})")
                    
        elif opcao == "4":
            print("\n--- Simulação de Divergência de Preço ---")
            id_prod = input("Digite o ID do produto para alterar o preço no sistema: ")
            try:
                novo_preco = float(input("Digite o novo preço (Ex: 150.00): "))
                produto_encontrado = None
                for loja in app.lojas.values():
                    for p in loja.catalogo:
                        if p.id_produto == id_prod:
                            produto_encontrado = p
                            break
                
                if produto_encontrado:
                    produto_encontrado.alterar_preco(novo_preco)
                    print(f"Preço do '{produto_encontrado.nome}' alterado para R${novo_preco:.2f}.")
                    print("Dica: Tente finalizar a compra agora para ver o bloqueio atuar.")
                else:
                    print("Produto não encontrado.")
            except ValueError:
                print("Erro: O preço deve ser um número (use ponto para decimais).")
                
        elif opcao == "5":
            print("\n--- Processando Checkout ---")
            resultado = app.finalizar_compra(cliente.id_usuario)
            print(resultado)
            
        elif opcao == "6":
            print("\n--- Histórico de Pedidos ---")
            if not cliente.historico_pedidos:
                print("Nenhum pedido realizado ainda.")
            else:
                for pedido in cliente.historico_pedidos:
                    print(pedido)

        elif opcao == "7":
            print("\n--- Cadastro de Nova Loja ---")
            nome_loja = input("Digite o nome da loja: ")
            nome_vendedor = input("Digite o nome do vendedor: ")
            app.criar_loja(nome_loja, nome_vendedor)
            print(f"Sucesso: Loja '{nome_loja}' criada!")

        elif opcao == "8":
            print("\n--- Publicar Produto ---")
            if not app.lojas:
                print("Erro: Nenhuma loja cadastrada. Crie uma loja primeiro (Opção 7).")
            else:
                print("Lojas disponíveis no sistema:")
                for nome in app.lojas.keys():
                    print(f"- {nome}")
                
                loja_escolhida = input("\nDigite o nome da loja onde quer publicar o produto: ")
                
                if loja_escolhida in app.lojas:
                    loja = app.lojas[loja_escolhida]
                    id_prod = input("Digite um ID para o produto (Ex: 3): ")
                    nome_prod = input("Digite o nome do produto: ")
                    try:
                        preco_prod = float(input("Digite o preço (Ex: 50.00): "))
                        estq_prod = int(input("Digite a quantidade em estoque: "))
                        loja.publicar_produto(id_prod, nome_prod, preco_prod, estq_prod)
                        print(f"Sucesso: Produto '{nome_prod}' publicado na loja '{loja_escolhida}'!")
                    except ValueError:
                        print("Erro: Preço deve ser número e estoque deve ser inteiro.")
                else:
                    print("Erro: Loja não encontrada.")
                    
        else:
            print("Opção inválida. Tente novamente.")
