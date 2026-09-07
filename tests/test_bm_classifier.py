"""
Testes unitários para os classificadores determinísticos de BmGroup e RelintType.
"""
import pytest
from backend.engine.cleaners.bm_classifier import classify_bm_group, classify_relint_type


class TestBmClassifier:
    """Testes de classificação correta por padrões do arquivo e assunto."""

    # --- Homicídio ---
    def test_homicidio_por_filename(self):
        result = classify_bm_group(filename="RELINT 467 - Homicídio Doloso em Panambi - RS.pdf")
        assert result == "Homicídio"

    def test_homicidio_por_subject(self):
        result = classify_bm_group(subject="HOMICÍDIO DOLOSO EM PANAMBI - RS")
        assert result == "Homicídio"

    def test_homicidio_tentativa_por_subject(self):
        result = classify_bm_group(subject="Tentativa de Homicídio em Palmeira das Missões")
        assert result == "Homicídio"

    def test_feminicidio_por_subject(self):
        result = classify_bm_group(subject="Feminicídio em Ijuí - RS")
        assert result == "Homicídio"

    def test_latrocinio_por_subject(self):
        result = classify_bm_group(subject="Latrocínio - Santa Rosa RS")
        assert result == "Homicídio"

    def test_obito_por_content(self):
        result = classify_bm_group(
            subject="Ocorrência policial",
            content="Constatou-se o óbito da vítima no local."
        )
        assert result == "Homicídio"

    # --- Tráfico ---
    def test_trafico_por_subject(self):
        result = classify_bm_group(subject="Prisão por Tráfico de Drogas em Cruz Alta")
        assert result == "Prisão por Tráfico"

    def test_trafico_por_content(self):
        result = classify_bm_group(
            subject="Ocorrência Policial",
            content="Foram apreendidos 30g de crack e 50g de maconha durante abordagem."
        )
        assert result == "Prisão por Tráfico"

    # --- Roubo a Estabelecimento ---
    def test_roubo_estabelecimento_por_subject(self):
        result = classify_bm_group(subject="Roubo a Estabelecimento Comercial em Panambi")
        assert result == "Roubo a Estabelecimento"

    def test_roubo_banco_por_subject(self):
        result = classify_bm_group(subject="Roubo ao Banco do Brasil em Santa Rosa")
        assert result == "Roubo a Estabelecimento"

    # --- Roubo a Residência ---
    def test_roubo_residencia_por_subject(self):
        result = classify_bm_group(subject="Roubo a Residencia na Rua das Flores")
        assert result == "Roubo a Residência"

    def test_roubo_residencia_acentuado(self):
        result = classify_bm_group(subject="Roubo à Residência")
        assert result == "Roubo a Residência"

    # --- Roubo de Veículo ---
    def test_roubo_veiculo_por_subject(self):
        result = classify_bm_group(subject="Roubo de Veículo - GM Onix - Cruz Alta RS")
        assert result == "Roubo de Veículo"

    def test_roubo_moto_por_subject(self):
        result = classify_bm_group(subject="Roubo de Motocicleta Panambi")
        assert result == "Roubo de Veículo"

    # --- Roubo a Pedestre ---
    def test_roubo_pedestre_por_subject(self):
        result = classify_bm_group(subject="Roubo a Pedestre - Centro Palmeira das Missões")
        assert result == "Roubo a Pedestre"

    def test_roubo_celular_por_subject(self):
        result = classify_bm_group(subject="Roubo de Celular - Palmeira das Missões")
        assert result == "Roubo a Pedestre"

    # --- Furto de Veículo ---
    def test_furto_veiculo_por_subject(self):
        result = classify_bm_group(subject="Furto de Veículo - Peugeot 208 - Ijuí RS")
        assert result == "Furto de Veículo"

    # --- Furto Qualificado ---
    def test_furto_qualificado_por_subject(self):
        result = classify_bm_group(subject="Furto Qualificado mediante arrombamento")
        assert result == "Furto Qualificado"

    def test_furto_simples_por_subject(self):
        result = classify_bm_group(subject="Furto em estabelecimento comercial")
        assert result == "Furto Qualificado"

    # --- Outros / Fallback ---
    def test_outros_quando_nada_bate(self):
        result = classify_bm_group(filename="RELINT-001.pdf", subject="Ocorrência diversa")
        assert result == "Outros"

    def test_nao_confia_em_palpite_livre_da_llm(self):
        """
        Nunca deve haver um 3º fallback que preserve um palpite livre da LLM.
        100% determinístico: regex bateu ou "Outros", nunca um terceiro caminho.
        (bug real: 'Encontro de artefato explosivo' foi classificado como 'Roubo a
        Estabelecimento' porque o antigo fallback preservava a resposta legada não
        confiável da LLM quando as 2 camadas de regex não encontravam nada.)
        """
        result = classify_bm_group(
            filename="RELATÓRIO DE INTELIGÊNCIA Nº 424/2026/ADJ-CI",
            subject="Encontro de artefato explosivo em Cruz Alta - RS",
            content="A guarnição isolou o local e removeu o artefato para detonação."
        )
        assert result == "Outros"

    # --- Prioridade: Homicídio > Tráfico ---
    def test_homicidio_prevalece_sobre_trafico(self):
        """Latrocínio envolve tráfico e morte; deve classificar como Homicídio."""
        result = classify_bm_group(
            subject="Latrocínio - vítima fatal - droga"
        )
        assert result == "Homicídio"


class TestRelintTypeClassifier:
    """Testes de classificação determinística do RelintType (Disk Denúncia, Resposta a PB, Ocorrência)."""

    # --- Resposta a PB (casos reais do dataset) ---
    def test_resposta_pb_por_filename(self):
        result = classify_relint_type(
            filename="RELINT 004 - ADJ-INT- CI - Resposta PB 8843 - Informação sobre Desaparecimento.pdf"
        )
        assert result == "Resposta a PB"

    def test_resposta_pb_colado_ao_numero(self):
        result = classify_relint_type(
            filename="RELINT 005 - ADJ-INT- CI - Resposta PB006 15 BPM - INFORMAÇÃO M.E.pdf"
        )
        assert result == "Resposta a PB"

    def test_resposta_pb_por_conteudo(self):
        result = classify_relint_type(
            subject="Ocorrência policial",
            content="Em resposta ao pedido de busca formulado pela unidade, informa-se que..."
        )
        assert result == "Resposta a PB"

    # --- Disk Denúncia (caso real do dataset) ---
    def test_disk_denuncia_por_filename(self):
        result = classify_relint_type(
            filename="RELINT 432 - ADJ-INT-CRIM - Repasse Disque Denúncia 123906-0070 - Outros, receptação em Seberi - RS.pdf"
        )
        assert result == "Disk Denúncia"

    def test_disk_denuncia_grafia_alternativa(self):
        result = classify_relint_type(subject="DISK DENÚNCIA ANÔNIMA - Tráfico de Drogas")
        assert result == "Disk Denúncia"

    # --- Ocorrência (fallback majoritário, não "Outros") ---
    def test_ocorrencia_quando_nada_bate(self):
        result = classify_relint_type(
            filename="RELINT 015 - ADJ-INT- CRIM - Homicídio em Seberi - RS.pdf",
            subject="Homicídio em Seberi - RS"
        )
        assert result == "Ocorrência"

    def test_ocorrencia_e_o_fallback_nao_outros(self):
        # Diferente de classify_bm_group: aqui o caso majoritário sem gatilho é "Ocorrência".
        result = classify_relint_type(filename="qualquer.pdf", subject="", content="")
        assert result == "Ocorrência"

    # --- Prioridade: filename+assunto vence sobre conteúdo ---
    def test_filename_prevalece_sobre_conteudo(self):
        result = classify_relint_type(
            filename="RELINT 432 - Repasse Disque Denúncia - Seberi - RS.pdf",
            subject="Receptação em Seberi - RS",
            content="Em resposta ao pedido de busca, nada mais consta."
        )
        assert result == "Disk Denúncia"
