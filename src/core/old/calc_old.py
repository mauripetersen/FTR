from Pynite import FEModel3D  # Import `FEModel3D` from `Pynite`

from math import sqrt, tan, pi, log


def dimensionar_viga_rc(
        # Geometria
        b_mm: float, d_mm: float, h_mm: float, d_linha_mm: float,
        # Esforços (ELU)
        Md: float, Vd: float,
        Md_kNm: bool = True, Vd_kN: bool = True,
        # Materiais
        fck: float = 30.0,  # MPa
        fyk: float = 500.0,  # MPa (CA-50)
        Es: float = 210000.0,  # MPa
        # Parâmetros de cálculo (NBR/EC2 – típicos)
        gamma_c: float = 1.4,
        gamma_s: float = 1.15,
        alpha_c: float = 0.85,  # bloco retangular
        lambda_: float = 0.80,  # profundidade do bloco
        alpha_cc: float = 1.00,  # fator de longo prazo (ajuste se preferir 0.85)
        # Domínios (deformações de cálculo)
        eps_cu: float = 3.5e-3,
        # Treliça de Mörsch
        theta_graus: float = 45.0,  # 30°–45° usual
        # Regras simplificadas NBR/EC2 (mínimos)
        h_skin_lim_mm: float = 600.0,  # armadura de pele se h >= 600 mm
        usar_regra_min_long_ec2: bool = True,  # As,min = max(0.26 fctm/fyk b d ; 0.0013 b d)
):
    """
    Protótipo de dimensionamento:
    - Decide simples/dupla.
    - Calcula As (e As' se necessário).
    - Checa mínimos longitudinais.
    - Dimensiona estribos (Mörsch).
    - Calcula armadura de pele quando h >= h_skin_lim_mm.

    Retorna um dicionário com resultados e sugestões.
    """

    # -------------------------------
    # 0) Conversões e resistências
    # -------------------------------
    M = Md * 1e6 if Md_kNm else Md  # kN·m -> N·mm
    V = Vd * 1e3 if Vd_kN else Vd  # kN   -> N

    fcd = alpha_cc * fck / gamma_c  # MPa
    fyd = fyk / gamma_s  # MPa
    eps_yd = fyd / Es  # adim.

    # fctm (NBR/EC2 – aproximação)
    if fck <= 50:
        fctm = 0.30 * (fck ** (2 / 3))  # MPa
    else:
        fcm = fck + 8.0
        fctm = 2.12 * log(1.0 + fcm / 10.0)  # MPa

    # -------------------------------
    # 1) Verifica simples x dupla
    #    (limite quando eps_s = eps_yd)
    # -------------------------------
    xi_lim = eps_cu / (eps_cu + eps_yd)  # x_lim / d
    x_lim = xi_lim * d_mm
    y_lim = lambda_ * x_lim / d_mm  # y = λ x / d
    z_lim = d_mm * (1.0 - 0.5 * y_lim)
    C_lim = alpha_c * fcd * b_mm * (y_lim * d_mm)  # αc fcd b (λx) = αc fcd b (y d)
    M_lim = C_lim * (1.0 - 0.5 * y_lim)  # = C * z/d * d = αc fcd b d^2 [y (1 - y/2)]

    # -------------------------------
    # 2) Caso 1 – Armadura simples (Md <= M_lim)
    #    Resolve y pela forma fechada: k = αc λ (y - y²/2)
    # -------------------------------
    resultados = {}
    k = M / (b_mm * (d_mm ** 2) * fcd)  # adim.
    k_lim = alpha_c * (y_lim - 0.5 * (y_lim ** 2))  # para conferir

    if k <= k_lim + 1e-12:
        # y = 1 - sqrt(1 - 2k/(αc λ))
        base = 1.0 - 2.0 * k / (alpha_c * lambda_)
        base = max(base, 0.0)  # robustez numérica
        y = 1.0 - sqrt(base)
        x = (y * d_mm) / lambda_
        z = d_mm * (1.0 - 0.5 * y)

        # Equilíbrio: T = C => As = C/fyd = αc fcd b (y d) / fyd
        As_req = (alpha_c * fcd * b_mm * (y * d_mm)) / fyd

        tipo = "simples"
        As_comp = 0.0
        x_usado = x
        z_usado = z
    else:
        # -------------------------------
        # 3) Caso 2 – Armadura dupla (Md > M_lim)
        # -------------------------------
        # Parte 1 (até x_lim): As1 = C_lim / fyd
        As1 = C_lim / fyd

        # Momento excedente
        delta_M = M - (alpha_c * fcd * b_mm * (d_mm ** 2) * (y_lim - 0.5 * (y_lim ** 2)))

        # Supõe-se o par aço tração/compressão levando delta_M
        alavanca_dupla = max(d_mm - d_linha_mm, 1e-6)  # evita zero
        As2_trac = delta_M / (fyd * alavanca_dupla)

        # Verifica se aço comprimido escoa
        # Deformação no aço comprimido (adotando x = x_lim)
        eps_s_comp = eps_cu * max(x_lim - d_linha_mm, 0.0) / max(x_lim, 1e-9)
        sig_s_comp = min(Es * eps_s_comp, fyd)  # MPa
        # Força de compressão no aço = As' * sig_s_comp = As2_trac * fyd  => As'
        As_comp = As2_trac * (fyd / max(sig_s_comp, 1e-9))

        As_req = As1 + As2_trac
        tipo = "dupla"
        x_usado = x_lim
        z_usado = d_mm * (1.0 - 0.5 * y_lim)

    # -------------------------------
    # 4) Mínimo longitudinal (aprox. NBR/EC2)
    # -------------------------------
    if usar_regra_min_long_ec2:
        As_min_1 = 0.26 * (fctm / fyk) * b_mm * d_mm
        As_min_2 = 0.0013 * b_mm * d_mm
        As_min = max(As_min_1, As_min_2)
    else:
        # alternativa simples (antiga) 0,15% bw*d
        As_min = 0.0015 * b_mm * d_mm

    As_prov = max(As_req, As_min)

    # -------------------------------
    # 5) Treliça de Mörsch (estribos)
    #     V_Rd,s = (Asw/s) * z * fyd * cot θ  =>  Asw/s = Vd / (z fyd cot θ)
    # -------------------------------
    theta_rad = theta_graus * 3.141592653589793 / 180.0
    cot_theta = 1.0 / tan(theta_rad)

    # Se não saiu z do simples, usa z ≈ 0.9 d (conservador/usuais)
    z_para_cisalhamento = z_usado if z_usado > 0 else 0.9 * d_mm

    Asw_s_req = V / (max(z_para_cisalhamento, 1e-6) * fyd * max(cot_theta, 1e-6))  # mm²/mm

    # Mínimo de cisalhamento (aprox. NBR/EC2): (Asw/s)_min = 0.2 * b_w * fctm / fyd
    Asw_s_min = 0.2 * b_mm * (fctm / fyd)
    Asw_s_prov = max(Asw_s_req, Asw_s_min)

    # Limites usuais de espaçamento (orientativo): s <= min(0.5 d, 300 mm)
    s_max_mm = min(0.5 * d_mm, 300.0)

    # Função auxiliar para sugerir espaçamento dado φ e nº de ramos (2 ramos = estribo comum)
    def sugerir_espacamento(phi_mm: float = 5.0, n_ramos: int = 2):
        area_barra = (pi * (phi_mm ** 2)) / 4.0
        Asw_por_estribo = n_ramos * area_barra
        s_mm = max(Asw_por_estribo / max(Asw_s_prov, 1e-9), 1.0)  # mm
        return {
            "phi_mm": phi_mm,
            "n_ramos": n_ramos,
            "s_sugerido_mm": min(s_mm, s_max_mm),
            "s_max_mm": s_max_mm,
            "Asw_s_prov_mm2_por_mm": Asw_s_prov,
            "Asw_por_estribo_mm2": Asw_por_estribo
        }

    # -------------------------------
    # 6) Armadura de pele (quando h >= 600 mm) – regra simples
    #     As_skin_total ≈ 0.10% * b * h (distribuída nas faces tracionadas)
    # -------------------------------
    As_skin_total = 0.0
    As_skin_por_face = 0.0
    if h_mm >= h_skin_lim_mm:
        As_skin_total = 0.0010 * b_mm * h_mm
        As_skin_por_face = 0.5 * As_skin_total

    # -------------------------------
    # 7) Saída
    # -------------------------------
    resultados.update({
        "tipo": tipo,  # "simples" ou "dupla"
        "Md_Nmm": M,
        "Vd_N": V,
        "fcd_MPa": fcd,
        "fyd_MPa": fyd,
        "fctm_MPa": fctm,
        "y_usado": (lambda_ * x_usado / d_mm) if x_usado > 0 else 0.0,
        "x_mm": x_usado,
        "z_mm": z_usado if z_usado > 0 else z_para_cisalhamento,
        "Md_lim_Nmm": M_lim,
        "As_req_mm2": As_req,
        "As_min_mm2": As_min,
        "As_prov_mm2": As_prov,
        "As_comp_mm2": As_comp if tipo == "dupla" else 0.0,
        "cisalhamento": {
            "theta_graus": theta_graus,
            "cot_theta": cot_theta,
            "z_para_cisalhamento_mm": z_para_cisalhamento,
            "Asw_s_req_mm2_por_mm": Asw_s_req,
            "Asw_s_min_mm2_por_mm": Asw_s_min,
            "Asw_s_prov_mm2_por_mm": Asw_s_prov,
            "s_max_mm": s_max_mm,
            "sugestao_estribo_fn": "use sugerir_espacamento(phi_mm, n_ramos)"
        },
        "pele": {
            "h_skin_lim_mm": h_skin_lim_mm,
            "As_skin_total_mm2": As_skin_total,
            "As_skin_por_face_mm2": As_skin_por_face
        },
        "observacoes": [
            "Adote unidades consistentes: N, mm, MPa, kN.",
            "Regras de mínimos e pele estão em forma simplificada (NBR/EC2). Ajuste se precisar da letra da NBR 6118:2023.",
            "Para armadura dupla, foi verificado escoamento no aço comprimido; se não escoar, o programa ajusta As'.",
            "Para estribos: escolha φ e nº de ramos e use sugerir_espacamento().",
        ]
    })

    # Anexa a função de sugestão dentro do resultado para uso direto (opcional)
    resultados["sugerir_espacamento"] = sugerir_espacamento

    return resultados


# -------------------------------
# Exemplo rápido de uso:
# -------------------------------
if __name__ == "__main__":
    out = dimensionar_viga_rc(
        b_mm=200, d_mm=450, h_mm=500, d_linha_mm=50,
        Md=120, Vd=130,  # Md=120 kN·m; Vd=130 kN
        Md_kNm=True, Vd_kN=True,
        fck=30, fyk=500
    )
    print(f"Tipo: {out['tipo']}")
    print(f"As,prov (mm²): {out['As_prov_mm2']:.1f}")
    if out["tipo"] == "dupla":
        print(f"As' (mm²): {out['As_comp_mm2']:.1f}")
    print(f"(Asw/s)_prov (mm²/mm): {out['cisalhamento']['Asw_s_prov_mm2_por_mm']:.3f}")
    # Sugestão de estribo φ5 c/ 2 ramos:
    sug = out["sugerir_espacamento"](phi_mm=5.0, n_ramos=2)
    print(
        f"Espaçamento sugerido φ{int(sug['phi_mm'])} c/{sug['n_ramos']} ramos: {sug['s_sugerido_mm']:.0f} mm (máx {sug['s_max_mm']:.0f} mm)")
    if out["pele"]["As_skin_total_mm2"] > 0:
        print(
            f"As de pele total: {out['pele']['As_skin_total_mm2']:.1f} mm² (≈ {out['pele']['As_skin_por_face_mm2']:.1f} por face)")
