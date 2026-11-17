"""Usuário gravado nas colunas de auditoria."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioAuditoria:
    """Nome e RF de quem criou ou alterou um registro."""

    nome: str
    rf: str


SISTEMA = UsuarioAuditoria(nome="Sistema", rf="0")
