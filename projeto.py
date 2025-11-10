import csv
import os
import re
import sys
from datetime import datetime

VALOR_APARTAMENTO = 700.0
VALOR_CASA = 900.0
VALOR_ESTUDIO = 1200.0

ACRESCIMO_QUARTO_APT_2 = 200.0
ACRESCIMO_QUARTO_CASA_2 = 250.0
ACRESCIMO_GARAGEM_APT_CASA = 300.0
ESTUDIO_2_VAGAS = 250.0
ESTUDIO_VAGA_EXTRA = 60.0

DESCONTO_APT_SEM_FILHOS = 0.05  

VALOR_CONTRATO = 2000.0
PARCELAS_CONTRATO_MIN = 1
PARCELAS_CONTRATO_MAX = 5


def money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def sanitize_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    if not name:
        name = "cliente"
    return name

def calcular_valor_base(tipo: str) -> float:
    tipo = tipo.lower()
    if tipo == "apartamento":
        return VALOR_APARTAMENTO
    if tipo == "casa":
        return VALOR_CASA
    if tipo == "estudio" or tipo == "estúdio":
        return VALOR_ESTUDIO
    raise ValueError("Tipo de imóvel inválido")


def aplicar_quartos_e_acrescimos(tipo: str, quartos: int, garagem: bool, estudio_vagas: int) -> float:
    base = calcular_valor_base(tipo)

    if tipo == "apartamento" and quartos == 2:
        base += ACRESCIMO_QUARTO_APT_2
    if tipo == "casa" and quartos == 2:
        base += ACRESCIMO_QUARTO_CASA_2

    if (tipo == "apartamento" or tipo == "casa") and garagem:
        base += ACRESCIMO_GARAGEM_APT_CASA

    if tipo == "estudio" or tipo == "estúdio":
        if estudio_vagas <= 0:
            pass
        else:
            if estudio_vagas <= 2:
                base += ESTUDIO_2_VAGAS
            else:
                extra = estudio_vagas - 2
                base += ESTUDIO_2_VAGAS + extra * ESTUDIO_VAGA_EXTRA

    return base


def aplicar_desconto(tipo: str, valor: float, tem_filhos: bool) -> float:
    if tipo == "apartamento" and not tem_filhos:
        return valor * (1 - DESCONTO_APT_SEM_FILHOS)
    return valor


def calcular_parcela_contrato(num_parcelas: int) -> float:
    if num_parcelas < PARCELAS_CONTRATO_MIN or num_parcelas > PARCELAS_CONTRATO_MAX:
        raise ValueError(f"Parcelas do contrato devem ser entre {PARCELAS_CONTRATO_MIN} e {PARCELAS_CONTRATO_MAX}.")
    return VALOR_CONTRATO / num_parcelas

def gerar_csv(aluguel_mensal: float, parcela_contrato: float, num_parcelas_contrato: int, filename: str):
    headers = ["mes", "aluguel_mensal", "parcela_contrato", "total_no_mes"]

    with open(filename, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for mes in range(1, 13):
            parcela = parcela_contrato if mes <= num_parcelas_contrato else 0.0
            total = aluguel_mensal + parcela
            writer.writerow([mes, f"{aluguel_mensal:.2f}", f"{parcela:.2f}", f"{total:.2f}"])

def escolher_tipo() -> str:
    opções = {
        "1": "apartamento",
        "2": "casa",
        "3": "estudio",
    }
    while True:
        print("Escolha o tipo de imóvel:")
        print("  1) Apartamento (R$ 700,00)")
        print("  2) Casa (R$ 900,00)")
        print("  3) Estúdio (R$ 1.200,00)")
        escolha = input("Digite 1, 2 ou 3: ").strip()
        if escolha in opções:
            return opções[escolha]
        print("Opção inválida — tente novamente.\n")


def perguntar_sim_nao(pergunta: str) -> bool:
    while True:
        resp = input(pergunta + " (s/n): ").strip().lower()
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False
        print("Resposta inválida — digite 's' para sim ou 'n' para não.")


def input_int(prompt_text: str, allowed: tuple | None = None) -> int:
    while True:
        val = input(prompt_text).strip()
        if not val.isdigit():
            print("Por favor, digite um número inteiro.")
            continue
        ival = int(val)
        if allowed and ival not in allowed:
            print(f"Valor inválido. Valores permitidos: {allowed}")
            continue
        return ival


def main():
    print("--- Sistema CLI de Orçamento — Imobiliária R.M. ---\n")

    nome = input("Nome do cliente: ").strip()
    if not nome:
        print("Nome inválido. Encerrando.")
        sys.exit(1)

    tipo = escolher_tipo()

    quartos = 1
    estudio_vagas = 0
    garagem = False

    if tipo in ("apartamento", "casa"):
        quartos = input_int("Quantidade de quartos (1 ou 2): ", allowed=(1, 2))
        garagem = perguntar_sim_nao("Deseja vaga(s) de garagem?")
    else: 
        estudio_vagas = input_int("Quantas vagas de estacionamento? (0 para nenhuma): ")

    tem_filhos = perguntar_sim_nao("O cliente possui filhos?")

    while True:
        num_parcelas_contrato = input_int(f"Em quantas parcelas deseja dividir o contrato (de {PARCELAS_CONTRATO_MIN} a {PARCELAS_CONTRATO_MAX})?: ")
        if PARCELAS_CONTRATO_MIN <= num_parcelas_contrato <= PARCELAS_CONTRATO_MAX:
            break
        print("Número de parcelas inválido.")

    valor_com_acrescimos = aplicar_quartos_e_acrescimos(tipo, quartos, garagem, estudio_vagas)
    valor_com_desconto = aplicar_desconto(tipo, valor_com_acrescimos, tem_filhos)

    parcela_contrato = calcular_parcela_contrato(num_parcelas_contrato)

    print("\n--- Resumo do Orçamento ---")
    print(f"Cliente: {nome}")
    print(f"Tipo: {tipo.capitalize()}")
    if tipo in ("apartamento", "casa"):
        print(f"Quartos: {quartos}")
        print(f"Vaga(s) de garagem: {'Sim' if garagem else 'Não'}")
    else:
        print(f"Vagas solicitadas (estúdio): {estudio_vagas}")

    print(f"Valor do aluguel mensal (após acréscimos/descontos): {money(valor_com_desconto)}")
    print(f"Valor do contrato: {money(VALOR_CONTRATO)}")
    print(f"Parcelamento do contrato: {num_parcelas_contrato}x de {money(parcela_contrato)}")

    gerar = perguntar_sim_nao("Deseja gerar um arquivo .csv com 12 parcelas do orçamento? (serão listados os 12 meses, com as parcelas do contrato apenas nos primeiros meses)")
    if gerar:
        safe_name = sanitize_filename(nome)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"orcamento_{safe_name}_{timestamp}.csv"
        gerar_csv(valor_com_desconto, parcela_contrato, num_parcelas_contrato, filename)
        abspath = os.path.abspath(filename)
        print(f"CSV gerado: {abspath}")

    print("\nOrçamento concluído. Obrigado!")


if __name__ == "__main__":
    main()
