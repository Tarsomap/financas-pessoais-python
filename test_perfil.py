"""
test_perfil.py — Testa a hierarquia de perfis polimórficos (Frente 2).

Conceitos cobertos:
    - ABC impede instância direta de Perfil
    - PessoaFisica e Empresa implementam o contrato corretamente
    - A factory criar_perfil devolve o tipo certo a partir de um texto
    - Polimorfismo: o código chama o mesmo método em objetos diferentes
"""

import pytest
from models.perfil import Perfil, PessoaFisica, Empresa, criar_perfil


class TestPerfilAbstrato:
    """Perfil é uma classe abstrata — não pode ser instanciada diretamente."""

    def test_instanciar_perfil_diretamente_deve_falhar(self):
        """
        pytest.raises é um gerenciador de contexto que ESPERA uma exceção.
        Se a exceção não ocorrer, o teste FALHA — o comportamento oposto do
        que intuitivamente parece.

        Por que TypeError? O Python lança TypeError ao tentar instanciar
        uma ABC com métodos abstratos não implementados.
        """
        with pytest.raises(TypeError):
            Perfil()  # deve explodir — ABC não pode ser instanciada

    def test_pessoa_fisica_e_subclasse_de_perfil(self):
        """isinstance verifica a hierarquia de herança."""
        pf = PessoaFisica()
        assert isinstance(pf, Perfil)

    def test_empresa_e_subclasse_de_perfil(self):
        emp = Empresa()
        assert isinstance(emp, Perfil)


class TestPessoaFisica:

    def test_tipo_str_retorna_pessoa_fisica(self):
        pf = PessoaFisica()
        assert pf.tipo_str() == "pessoa_fisica"

    def test_categorias_disponiveis_e_lista_nao_vazia(self):
        pf = PessoaFisica()
        cats = pf.categorias_disponiveis()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_categorias_sao_strings(self):
        """Cada categoria deve ser um texto — templates HTML dependem disso."""
        pf = PessoaFisica()
        for cat in pf.categorias_disponiveis():
            assert isinstance(cat, str), f"Categoria '{cat}' não é string"


class TestEmpresa:

    def test_tipo_str_retorna_empresa(self):
        emp = Empresa()
        assert emp.tipo_str() == "empresa"

    def test_categorias_disponiveis_e_lista_nao_vazia(self):
        emp = Empresa()
        cats = emp.categorias_disponiveis()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_categorias_de_empresa_diferem_de_pessoa_fisica(self):
        """
        Polimorfismo real: o mesmo método retorna dados diferentes
        dependendo do objeto concreto. Se os dois devolverem a mesma lista,
        o polimorfismo não está funcionando.
        """
        pf = PessoaFisica()
        emp = Empresa()
        assert pf.categorias_disponiveis() != emp.categorias_disponiveis()


class TestFactory:
    """A factory criar_perfil lê um texto e devolve o objeto certo."""

    def test_factory_com_pessoa_fisica(self):
        perfil = criar_perfil("pessoa_fisica")
        assert isinstance(perfil, PessoaFisica)

    def test_factory_com_empresa(self):
        perfil = criar_perfil("empresa")
        assert isinstance(perfil, Empresa)

    def test_factory_com_tipo_invalido_deve_falhar(self):
        """
        Tipo desconhecido deve levantar ValueError — não retornar None
        silenciosamente, o que causaria bugs difíceis de rastrear.
        """
        with pytest.raises(ValueError):
            criar_perfil("tipo_inexistente")

    def test_factory_retorna_objeto_com_contrato_completo(self):
        """
        A factory deve devolver objeto que cumpre o contrato do Perfil:
        tem tipo_str() e categorias_disponiveis().
        """
        for tipo in ["pessoa_fisica", "empresa"]:
            perfil = criar_perfil(tipo)
            assert hasattr(perfil, "tipo_str")
            assert hasattr(perfil, "categorias_disponiveis")
            assert callable(perfil.tipo_str)
            assert callable(perfil.categorias_disponiveis)
