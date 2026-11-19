"""Erro de regra de negócio compartilhado entre os apps."""

from collections.abc import Iterable


class ErroDominio(Exception):  # noqa: N818
    """Regra de negócio que impede a operação."""

    def __init__(
        self,
        codigo: str,
        mensagem: str,
        detalhes: Iterable[object] | None = None,
    ) -> None:
        """Cria o erro.

        Args:
            codigo: Código do erro, para quem chama tratar cada caso.
            mensagem: Texto que pode ser mostrado ao usuário.
            detalhes: O que causou o erro, como as violações de uma
                validação.
        """
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhes = list(detalhes or [])
