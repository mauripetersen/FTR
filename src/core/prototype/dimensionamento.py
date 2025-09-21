import math


def dimensionar_viga_ca(
        # Geometria (m)
        bw_m: float, h_m: float, d_m: float, dp_m: float, L_m: float,
        # Esforços característicos - Solicitações Internas (kN, kN·m)
        Vk_kN: float, Mk_kNm: float,
        # Materiais
        fck_MPa: float = 30.0,  # fck [MPa]
        fyk_MPa: float = 500.0,  # fyk [MPa] CA-50 -> 500 MPa
        Ec_MPa: float = 25_000.0,  # Módulo de Elasticidade do concreto [MPa] ~25 MPa
        Es_MPa: float = 210_000.0,  # Módulo de Elasticidade do aço [MPa] ~210 GPa -> 210.000 MPa
        # Parâmetros de cálculo (NBR 6118)
        data_j: int = 28,  # data da verificação
        cimento: str = "CP II",  # tipo de cimento ("CP I", "CP II", "CP III", "CP IV" e "CP V-ARI")
        alpha_E: float = 1.0,  # fator do agregado graúdo (0.7, 0.9, 1.0 e 1.2) - NBR 6118:2023 Item 8.2.8
        CAA: int = 2,  # Classe de Agressividade Ambiental - NBR 6118:2023 Tabela 6.1
        cob_cm: float | None = 3,  # cobrimento - NBR 6118:2023 Tabela 7.2
        gamma_c: float = 1.4,
        gamma_s: float = 1.15,
        gamma_f: float = 1.4,  # coeficiente de majoração das ações
        alpha_c: float = 0.85,  # fator tradicional do bloco retangular
        lambda_c: float = 0.80,  # fator de profundidade do bloco (λ_c)
        # Cisalhamento (treliça de Mörsch)
        theta_deg: float = 45.0,  # 30–45° usual
        alpha_deg: float = 90.0,  # 90° usual (estribo vertical)
        # Armadura de pele (regra prática)
        lim_h_pele_m: float = 0.6,  # exigir pele se h > 60 cm
        # flecha já calculada externamente
        flecha_imediata_m: float | None = None,  # δ_max em metros
        limite_flecha_L_sobre: float = 250.0,  # verifica L/250 por padrão
):
    """
    Dimensionamento de viga de CA (ELU + verificação de flecha no ELS).

    Parâmetros
    ----------
    b_m, h_m, d_m, dp_m, L_m : float
        Geometria em metros (b = largura; d = altura útil tracionada; h = altura total; dp = d' comprimida; L = vão).
    Vk_kN, Mk_kNm : float
        Momento e cortante de cálculo (ELU), já com ações majoradas.
    fck_kNm2, fyk_kNm2 : float
        Resistências características (kN/m²).
    Es_kNm2 : float
        Módulo do aço (kN/m²).
    alpha_c, eta_c, lambda_c : float
        Parâmetros do bloco retangular (NBR 6118: item 8.2.10.1).
    flecha_imediata_m : float
        Flecha imediata máxima (m), vinda do modelo.

    Retorna
    -------
    dict
        Dicionário com resultados (As, As', mínimos, cisalhamento, pele, flecha, etc.).
    """

    if flecha_imediata_m is None:
        raise ValueError("Informe flecha_m (em metros)")

    # majoração das cargas
    Md_kNm = gamma_f * Mk_kNm
    Vd_kN = gamma_f * Vk_kN

    # --- Resistências
    # Resistência à tração do concreto (fctm)
    if fck_MPa <= 50:
        fctm_MPa = 0.3 * fck_MPa ** (2.0 / 3.0)
    else:
        fctm_MPa = 2.12 * math.log(1.0 + (fck_MPa + 8.0) / 10.0)
    fctk_inf_MPa = 0.7 * fctm_MPa
    fctk_sup_MPa = 1.3 * fctm_MPa

    # Resistência característica e de cálculo ao escoamento do aço dos estribos
    fywk_MPa = fyk_MPa
    fywd_MPa = min(fywk_MPa / gamma_s, 435.0)

    # Resistências de cálculo ("d" = "design")
    if data_j >= 28:
        beta_1 = 1.0
    else:
        if cimento in ["CP I", "CP II"]:
            s = .25
        elif cimento in ["CP III", "CP IV"]:
            s = .38
        elif cimento == "CP V-ARI":
            s = .2
        else:
            s = .25
        beta_1 = math.exp(s * (1 - math.sqrt((28 / data_j))))
    fcd_MPa = beta_1 * fck_MPa / gamma_c
    fyd_MPa = fyk_MPa / gamma_s

    # conversões MPa -> kN/m²
    fck_kNm2 = fck_MPa * 1e3
    fyk_kNm2 = fyk_MPa * 1e3
    fctm_kNm2 = fctm_MPa * 1e3
    fctk_inf_kNm2 = fctk_inf_MPa * 1e3
    fctk_sup_kNm2 = fctk_sup_MPa * 1e3
    fywk_kNm2 = fywk_MPa * 1e3
    fywd_kNm2 = fywd_MPa * 1e3
    fcd_kNm2 = fcd_MPa * 1e3
    fyd_kNm2 = fyd_MPa * 1e3
    Es_kNm2 = Es_MPa * 1e3

    # deformações
    # εc2 = eps_c2 = deformação específica de encurtamento do concreto no início do patamar plástico
    # εcu = eps_cu = deformação específica de encurtamento do concreto na ruptura
    # εyd = eps_yd = deformação de escoamento do aço
    if fck_MPa <= 50:
        eps_c2 = 2.0e-3
        eps_cu = 3.5e-3
    else:
        eps_c2 = 2.0e-3 + 0.085e-3 * (fck_MPa - 50) ** 0.53
        eps_cu = 2.6e-3 + 35e-3 * ((90 - fck_MPa) / 100) ** 4
    eps_yd = fyd_kNm2 / Es_kNm2

    # eta_c (novo, NBR 6118:2023)
    if fck_MPa <= 40:
        eta_c = 1.0
    else:
        eta_c = (40 / fck_MPa) ** (1 / 3)

    # Tensão reduzida no concreto
    sigma_cd_kNm2 = alpha_c * eta_c * fcd_kNm2

    # Momento reduzido
    mu = Md_kNm / (sigma_cd_kNm2 * bw_m * d_m ** 2)

    # Limites por deformações (domínio)
    xi_lim_2 = eps_cu / (eps_cu + 10.0e-3)
    xi_lim_3 = eps_cu / (eps_cu + eps_yd)
    if fck_MPa <= 50:
        xi_lim_nbr = 0.45
    else:
        xi_lim_nbr = 0.35
    xi_lim = min(xi_lim_3, xi_lim_nbr)
    x_lim_m = xi_lim * d_m
    y_lim_m = lambda_c * x_lim_m
    z_lim_m = d_m - y_lim_m / 2
    mu_lim = lambda_c * xi_lim * (1 - lambda_c * xi_lim / 2)  # momento limite reduzido

    # Cálculo de armaduras
    if mu <= mu_lim + 1e-12:
        # Armadura simples:
        base = max(1 - 2 * mu, 0)
        xi = (1 / lambda_c) * (1 - math.sqrt(base))
        As1_m2 = lambda_c * xi * bw_m * d_m * sigma_cd_kNm2 / fyd_kNm2
        As2_m2 = 0.0
        tipo = "simples"
    else:
        # Armadura dupla:
        xi = xi_lim
        delta = dp_m / d_m
        As1_m2 = (lambda_c * xi + (mu - mu_lim) / (1 - delta)) * (bw_m * d_m * sigma_cd_kNm2 / fyd_kNm2)
        As2_m2 = (mu - mu_lim) * bw_m * d_m * sigma_cd_kNm2 / ((1 - delta) * fyd_kNm2)
        tipo = "dupla"

    x_m = xi * d_m
    y_m = lambda_c * x_m
    z_m = d_m - y_m / 2

    # alongamento do aço
    eps_s = eps_cu * (d_m - x_m) / max(x_m, 1e-12)
    # print("eps_c2: ", eps_c2 * 1000)
    # print("eps_cu: ", eps_cu * 1000)
    # print("eps_yd: ", eps_yd * 1000)
    # print("eps_s: ", eps_s * 1000)

    # Classificação de domínio (simplificada)
    if xi <= xi_lim_2:
        dominio = 2  # falha no alongamento do aço
    elif xi <= xi_lim_3:
        dominio = 3  # falha no encurtamento do concreto com aço escoado
    else:
        dominio = 4  # falha no encurtamento do concreto sem aço escoado (PROIBIDO! ruína súbita)

    # Armadura mínima longitudinal
    W_0 = (bw_m * (h_m ** 2)) / 6
    M_d_min_kNm = 0.8 * W_0 * fctk_sup_kNm2
    As1_min_1_m2 = M_d_min_kNm / (z_m * fyd_kNm2)
    As1_min_2_m2 = .0015 * bw_m * d_m
    As1_min_m2 = max(As1_min_1_m2, As1_min_2_m2)
    As1_prov_m2 = max(As1_m2, As1_min_m2)  # Área de aço provida

    # ARMADURA DE CISALHAMENTO (treliça de Mörsch):
    cot_theta = 1.0  # theta = 45°
    sin_alpha = 1.0  # alpha = 90°
    # Força cortante atuante:
    Vsd_kN = gamma_f * Vk_kN
    # Biela comprimida (VRd2):
    alpha_v2 = max(0.0, 1.0 - fck_MPa / 250.0)
    VRd2_kN = 0.27 * alpha_v2 * fcd_kNm2 * bw_m * d_m
    # (Asw/s) necessária e mínima:
    fctd_kNm2 = fctk_inf_kNm2 / gamma_c
    Vc_kN = max(0.0, 0.6 * fctd_kNm2 * bw_m * d_m)  # Parcela do concreto
    Asw_s_req_m2pm = max(0.0, (Vsd_kN - Vc_kN) / (0.9 * d_m * fywd_kNm2))  # [m²/m]
    Asw_s_min_m2pm = max(0.0, 0.2 * fctm_kNm2 * bw_m * sin_alpha / max(fywk_kNm2, 1e-12))  # [m²/m]
    Asw_s_prov_m2pm = max(Asw_s_req_m2pm, Asw_s_min_m2pm)

    # Limites de espaçamento: s_max = min(0,6·d; 0,30 m) ou min(0,3·d; 0,20 m)
    if Vsd_kN <= 0.67 * VRd2_kN:
        s_max_m = min(0.6 * d_m, 0.30)
    else:
        s_max_m = min(0.3 * d_m, 0.20)

    # ARMADURA DE PELE
    if h_m > lim_h_pele_m:
        As_pele_por_face_m2 = 0.001 * bw_m * h_m
    else:
        As_pele_por_face_m2 = 0.0

    # VERIFICAÇÃO DA FLECHA
    delta_xi = 2.0  # t0 = 0, t = inf
    rho_linha = As2_m2 / (bw_m * d_m)  # tacha de armadura comprimida
    alpha_f = delta_xi / (1 + 50 * rho_linha)
    flecha_els_m = alpha_f * flecha_imediata_m
    flecha_lim_m = L_m / limite_flecha_L_sobre
    flecha_ok = (flecha_els_m <= flecha_lim_m + 1e-12)

    # == Verificações/avisos de viabilidade ==
    avisos: list[str] = []

    # Condições de dutilidade (NBR 6118:2023 - Item 14.6.4.3)
    if fck_MPa <= 50:
        if xi > .45:
            avisos.append(
                f"Linha neutra acima do limite (x/d = {xi:.4f} > 0.45): Dutilidade comprometida. "
                "Sugestão: Aumentar bw, d, fck, reduzir Md, ou adotar armadura de compressão eficaz (dupla).")
    else:
        if xi > .35:
            avisos.append(
                f"Linha neutra acima do limite (x/d = {xi:.4f} > 0.35): Dutilidade comprometida. "
                "Sugestão: Aumentar bw, d, fck, reduzir Md, ou adotar armadura de compressão eficaz (dupla).")

    # Flexão – domínio
    if dominio == 2:
        avisos.append(
            "Flexão no domínio 2 (x <= x_lim_2): "
            "Falha no alongamento do aço; "
            "Sugestão: Aumentar alavanca interna (z) ou reduzir taxa de armadura para entrar no domínio 3.")
    elif dominio == 4:
        avisos.append(
            "Flexão no domínio 4 (x > x_lim_3): "
            "Falha no encurtamento do concreto SEM escoar o aço. "
            "Sugestão: Aumentar bw, d, fck, reduzir Md, ou adotar armadura de compressão eficaz (dupla).")

    # Flexão – momento acima do limite de seção simples
    if mu > mu_lim + 1e-9:
        avisos.append(
            "μ > μ_lim: exigiu armadura dupla.")
            # "Se a parcela comprimida As' ficar elevada, reestude a seção (d, bw, fck) ou redistribua esforços.")

    # Taxa máxima de armadura tracionada (NBR 6118:2023 Item 17.3.5.2.4)
    rho_max = .04
    rho_prov = (As1_prov_m2 + As2_m2) / (bw_m * h_m)
    if rho_prov > rho_max:
        avisos.append(
            f"Taxa de armadura tracionada ρ = {rho_prov * 100:.3f}% excedeu ρ_max = {rho_max * 100:.3f}%. "
            "Viabilidade comprometida! Sugestão: Aumente a seção, eleve fck ou reduza Md")

    # Cisalhamento – biela comprimida
    if Vsd_kN > VRd2_kN + 1e-9:
        avisos.append(
            "Vsd > VRd2: ruína da biela comprimida antes de escoar os estribos! "
            "Sugestão: Aumente d/bw, eleve fck ou reduza Vsd.")

    # Flecha ELS
    if flecha_els_m > flecha_lim_m + 1e-9:
        avisos.append(
            f"flecha (δ = {flecha_els_m * 100:.3f} cm) excede o limite permitido "
            f"(δ_lim = {flecha_lim_m * 100:.3f} cm) pelo critério L/250. "
            "Sugestão: aumentar a altura útil da seção, adotar maior inércia ou redistribuir o carregamento.")

    # Saída
    saida = {
        "dados": {
            "resistencia": {
                "fck_MPa": round(fck_MPa, 4),
                "fyk_MPa": round(fyk_MPa, 4),
                "fywk_MPa": round(fywk_MPa, 4),
                "fctm_MPa": round(fctm_MPa, 4),
                "fctk_inf_MPa": round(fctk_inf_MPa, 4),
                "fctk_sup_MPa": round(fctk_sup_MPa, 4),
                "gamma_c": round(gamma_c, 4),
                "gamma_s": round(gamma_s, 4),
                "data_j": data_j,
                "cimento": cimento,
                "beta_1": round(beta_1, 4),
                "fcd_MPa": round(fcd_MPa, 4),
                "fyd_MPa": round(fyd_MPa, 4),
                "fywd_MPa": round(fywd_MPa, 4)
            },
            "modulo_elasticidade": {
                "alpha_E": round(alpha_E, 4),
                "Ec_MPa": round(Ec_MPa, 4),
                "Es_MPa": round(Es_MPa, 4)
            },
            "cargas": {
                "gamma_f": round(gamma_f, 4),
                "Vd_kN": round(Vd_kN, 4),
                "Md_kNm": round(Md_kNm, 4)
            },
            "alpha_c": round(alpha_c, 4),
            "eta_c": round(eta_c, 4),
            "lambda_c": round(lambda_c, 4),
            "sigma_cd_MPa": round(sigma_cd_kNm2 / 1e3, 4),
            "CAA": CAA,
            "cob_cm": cob_cm,
            "dp_cm": round(dp_m * 100, 4),
            "d_cm": round(d_m * 100, 4),
            "xi_lim_2": round(xi_lim_2, 4),
            "xi_lim_3": round(xi_lim_3, 4),
            "xi_lim_nbr": round(xi_lim_nbr, 4),
            "xi_lim": round(xi_lim, 4),
            "xi": round(xi, 4),
            "x_cm": round(x_m * 100, 4),
            "y_cm": round(y_m * 100, 4),
            "z_cm": round(z_m * 100, 4),
            "mu": round(mu, 6),
            "mu_lim": round(mu_lim, 6)
        },
        "dimensionamento": {
            "avisos": avisos,
            "armadura": {
                "tipo": tipo,
                "domínio": dominio,
                "longitudinal": {
                    "As1_cm2": round(float(As1_m2 * 1e4), 4),
                    "As1_min_cm2": round(float(As1_min_m2 * 1e4), 4),
                    "As1_prov_cm2": round(float(As1_prov_m2 * 1e4), 4),
                    "As2_cm2": round(float(As2_m2 * 1e4), 4)
                },
                "pele": {
                    "lim_h_pele_cm": lim_h_pele_m * 100,
                    "As_pele_por_face_cm2": round(float(As_pele_por_face_m2 * 1e4), 4)
                },
                "cisalhamento": {
                    "theta_deg": theta_deg,
                    "cot_theta": cot_theta,
                    "alpha_deg": alpha_deg,
                    "sin_alpha": sin_alpha,
                    "Vsd_kN": round(Vsd_kN, 4),
                    "alpha_v2": round(alpha_v2, 4),
                    "VRd2_kN": round(VRd2_kN, 4),
                    "Vc_kN": round(Vc_kN, 4),
                    "Asw_s_req_cm2pm": round(Asw_s_req_m2pm * 1e4, 4),
                    "Asw_s_min_cm2pm": round(Asw_s_min_m2pm * 1e4, 4),
                    "Asw_s_prov_cm2pm": round(Asw_s_prov_m2pm * 1e4, 4),
                    "s_max_cm": round(s_max_m * 100, 4)
                }
            },
            "flecha": {
                "flecha_imediata_cm": round(float(flecha_imediata_m) * 100, 4),
                "alpha_f": round(float(alpha_f), 4),
                "flecha_els_cm": round(float(flecha_els_m) * 100, 4),
                "flecha_lim_cm": round(float(flecha_lim_m) * 100, 4),
                "critério": f"L/{int(limite_flecha_L_sobre)}",
                "ok?": bool(flecha_ok)
            }
        }
    }

    return saida
