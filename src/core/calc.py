import math


def dimensionar_viga_ca(
        # Geometria (m)
        bw_m: float, h_m: float, d_m: float, dp_m: float, L_m: float,
        # Esforços característicos - Solicitações Internas (kN, kN·m)
        Vk_kN: float, Mk_kNm: float,
        # Materiais (tensões em kN/m²)
        fck_kNm2: float = 30_000.0,  # ex.: 30 MPa -> 30.000 kN/m²
        fyk_kNm2: float = 500_000.0,  # ex.: CA-50 -> 500 MPa -> 500.000 kN/m²
        Es_kNm2: float = 210_000_000.0,  # ~210 GPa -> 210.000.000 kN/m²
        # Parâmetros de cálculo (NBR 6118)
        j_date: float = 28,  # data da verificação
        cimento: str = "CP II",  # tipo de cimento ("CP I", "CP II", "CP III", "CP IV" e "CP V-ARI")
        gamma_c: float = 1.4,
        gamma_s: float = 1.15,
        gamma_f: float = 1.4,  # coeficiente de majoração das ações
        alpha_c: float = 0.85,  # fator tradicional do bloco retangular
        lambda_c: float = 0.80,  # fator de profundidade do bloco (λ_c)
        eps_cu: float = 3.5e-3,  # deformação última do concreto
        # Cisalhamento (treliça de Mörsch)
        theta_deg: float = 45.0,  # 30–45° usual
        # Armadura de pele (regra prática)
        lim_h_pele_m: float = 0.6,  # exigir pele se h >= 0,60 m
        # Limites usuais
        rho_max: float = 0.04,  # ~4% (limite construtivo/funcional típico para vigas)
        # flecha já calculada externamente (ex.: PyNiteFEA)
        flecha_imediata_m: float | None = None,  # δ_max em metros (obrigatório aqui)
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

    # fctm a partir de fck
    fck_MPa = fck_kNm2 / 1000.0
    if fck_MPa <= 50:
        fctm_MPa = .3 * (fck_MPa ** (2.0 / 3.0))
    else:
        fcm = fck_MPa + 8.0
        fctm_MPa = 2.12 * math.log(1.0 + fcm / 10.0)
    fctm_kNm2 = fctm_MPa * 1000.0

    fctk_inf_kNm2 = 0.7 * fctm_kNm2
    fctk_sup_kNm2 = 1.3 * fctm_kNm2

    # Resistência característica e de cálculo ao escoamento do aço dos estribos
    fywk_kNm2 = fyk_kNm2
    fywd_kNm2 = min(fywk_kNm2 / gamma_s, 435_000.0)

    # Resistências de cálculo
    if j_date >= 28:
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
        beta_1 = math.exp(s * (1 - math.sqrt((28 / j_date))))

    fcd_kNm2 = beta_1 * fck_kNm2 / gamma_c  # kN/m²
    fyd_kNm2 = fyk_kNm2 / gamma_s  # kN/m²

    # eta_c (novo, NBR 6118:2023)
    if fck_MPa <= 40:
        eta_c = 1.0
    else:
        eta_c = (40 / fck_MPa) ** (1 / 3)

    # Tensão reduzida no concreto
    sigma_cd_kNm2 = 0.85 * eta_c * fcd_kNm2

    # Momento reduzido
    mu = Md_kNm / (sigma_cd_kNm2 * bw_m * d_m ** 2)

    # Limites por deformações (domínio)
    eps_yd = fyd_kNm2 / Es_kNm2  # deformação de escoamento do aço
    xi_lim = eps_cu / (eps_cu + eps_yd)
    x_lim_m = xi_lim * d_m
    y_lim = lambda_c * xi_lim
    z_lim_m = d_m * (1.0 - y_lim / 2)
    mu_lim = y_lim - (y_lim ** 2) / 2  # momento limite reduzido

    # Cálculo de armaduras
    if mu <= mu_lim + 1e-12:
        # Armadura simples: y = 1 - sqrt(1 - 2μ)
        base = 1.0 - 2.0 * mu
        base = max(base, 0.0)
        y = 1.0 - math.sqrt(base)
        x_m = (y * d_m) / lambda_c
        z_m = d_m * (1.0 - y / 2)
        xi = y / lambda_c
        As1_m2 = (alpha_c * xi * bw_m * d_m * sigma_cd_kNm2) / fyd_kNm2
        As2_m2 = 0.0
        tipo = "simples"
    else:
        # Armadura dupla (até y_lim + parcela excedente com aço tração/comp.)
        delta = dp_m / d_m
        As1_m2 = (y_lim + (mu - mu_lim) / (1 - delta)) * (bw_m * d_m * sigma_cd_kNm2 / fyd_kNm2)
        As2_m2 = ((mu - mu_lim) * bw_m * d_m * sigma_cd_kNm2) / ((1 - delta) * fyd_kNm2)
        x_m = x_lim_m
        z_m = z_lim_m
        y = lambda_c * x_m / d_m
        tipo = "dupla"

    # Estado de deformações no aço tracionado
    eps_s_trac = eps_cu * (d_m - x_m) / max(x_m, 1e-12)

    # Classificação de domínio (simplificada)
    if x_m <= x_lim_m and eps_s_trac >= eps_yd:
        dominio = 3
    elif x_m < x_lim_m and eps_s_trac < eps_yd:
        dominio = 2
    else:
        dominio = 4  # x > x_lim → domínio 4 (compressão)

    # Armadura mínima longitudinal
    W_0 = (bw_m * (h_m ** 2)) / 6
    M_d_min = 0.8 * W_0 * fctk_sup_kNm2
    As1_min_1 = M_d_min / (z_m * fyd_kNm2)
    As1_min_2 = .0015 * bw_m * d_m
    As1_min_m2 = max(As1_min_1, As1_min_2)
    As1_prov_m2 = max(As1_m2, As1_min_m2)  # Área de aço provida

    # ARMADURA DE PELE
    As_pele_por_face_m2 = 0.0
    if h_m > lim_h_pele_m:
        As_pele_por_face_m2 = 0.0010 * bw_m * h_m

    # ARMADURA DE CISALHAMENTO (treliça de Mörsch):
    fctd_kNm2 = fctk_inf_kNm2 / gamma_c
    cot_theta = 1.0  # theta = 45º
    Vc_kN = max(0.0, 0.6 * fctd_kNm2 * bw_m * d_m)  # Parcela do concreto

    # (Asw/s) necessária e mínima
    Vsd_kN = gamma_f * Vk_kN
    Asw_s_req_m2pm = max(0.0, (Vsd_kN - Vc_kN) / (0.9 * d_m * fywd_kNm2))  # [m²/m]
    sin_alpha = 1.0
    Asw_s_min_m2pm = max(0.0, 0.2 * fctm_kNm2 * bw_m * sin_alpha / max(fywk_kNm2, 1e-12))  # [m²/m]
    Asw_s_prov_m2pm = max(Asw_s_req_m2pm, Asw_s_min_m2pm)
    
    # Biela comprimida (VRd2)
    alpha_v2 = max(0.0, 1.0 - fck_MPa / 250.0)
    VRd2_kN = 0.27 * alpha_v2 * fcd_kNm2 * bw_m * d_m

    # Limites de espaçamento: s_max = min(0,6·d; 0,30 m) ou min(0,3·d; 0,20 m)
    if Vsd_kN <= 0.67 * VRd2_kN:
        s_max_m = min(0.6 * d_m, 0.30)
    else:
        s_max_m = min(0.3 * d_m, 0.20)

    # VERIFICAÇÃO DA FLECHA
    delta_xi = 2.0  # t0 = 0, t = inf
    rho_linha = As2_m2 / (bw_m * d_m)  # tacha de armadura comprimida
    alpha_f = delta_xi / (1 + 50 * rho_linha)
    flecha_els_m = alpha_f * flecha_imediata_m
    flecha_lim_m = L_m / limite_flecha_L_sobre
    flecha_ok = (flecha_els_m <= flecha_lim_m)

    # == Verificações/avisos de viabilidade ==
    avisos: list[str] = []
    
    # Flexão – domínio
    if dominio == 4:
        avisos.append(
            "Flexão no domínio 4 (x > x_lim): seção está compressão-controlada. "
            "Sugestão: Aumentar bw, d, fck, reduzir Md, ou adotar armadura de compressão eficaz (dupla).")
    elif dominio == 2:
        avisos.append(
            "Flexão no domínio 2 (aço não escoa): verifique ductilidade/abrangência de fissuração. "
            "Sugestão: Aumentar alavanca interna (z) ou reduzir taxa de armadura para entrar no domínio 3.")

    # Flexão – momento acima do limite de seção simples
    if mu > mu_lim + 1e-9:
        avisos.append(
            "μ > μ_lim → exigiu armadura dupla; "
            "Se a parcela comprimida As' ficar elevada, reestude a seção (d, bw, fck) ou redistribua esforços.")

    # Taxa máxima de armadura tracionada (limite construtivo/funcional típico)
    rho_prov = (As1_prov_m2 + As2_m2) / (bw_m * h_m)
    if rho_prov > rho_max:
        avisos.append(
            f"Taxa de armadura tracionada ρ = {rho_prov * 100:.3f}% excedeu ρ_max = {rho_max * 100:.3f}%. "
            "Viabilidade comprometida! Sugestão: Aumente a seção, eleve fck ou reduza Md")

    # Cisalhamento – biela comprimida
    if Vsd_kN > VRd2_kN + 1e-9:
        avisos.append(
            "Vsd > VRd2: ruína da biela comprimida antes de escoar os estribos! "
            "Sugestão: Aumente d/bw, eleve fck ou reduza Vd.")

    # Flecha ELS
    if flecha_els_m > flecha_lim_m + 1e-9:
        avisos.append(
            f"flecha (δ = {flecha_els_m * 100:.3f} cm) excede o limite permitido "
            f"(δ_lim = {flecha_lim_m * 100:.3f} cm) pelo critério L/250. "
            "Sugestão: aumentar a altura útil da seção, adotar maior inércia ou redistribuir o carregamento.")

    # Saída
    saida = {
        "dados": {
            "fck_MPa": round(fck_kNm2 / 1000, 4),
            "fyk_MPa": round(fyk_kNm2 / 1000, 4),
            "fywk_MPa": round(fywk_kNm2 / 1000, 4),
            "fctm_MPa": round(fctm_kNm2 / 1000, 4),
            "fctk_inf_MPa": round(fctk_inf_kNm2 / 1000, 4),
            "fctk_sup_MPa": round(fctk_sup_kNm2 / 1000, 4),
            "beta_1": round(beta_1, 4),
            "fcd_MPa": round(fcd_kNm2 / 1000, 4),
            "fyd_MPa": round(fyd_kNm2 / 1000, 4),
            "fywd_MPa": round(fywd_kNm2 / 1000, 4),
            "Vd_kN": Vd_kN, "Md_kNm": Md_kNm,
            "alpha_c": alpha_c,
            "eta_c": round(eta_c, 4),
            "lambda_c": lambda_c,
            "sigma_cd_kNm2": round(sigma_cd_kNm2, 4),
            "mu": round(mu, 8),
            "mu_lim": round(mu_lim, 8),
            "y": round(y, 8),
            "x_m": round(x_m, 8),
            "z_m": round(z_m, 8)
        },
        "dimensionamento": {
            "tipo": tipo,
            "domínio": dominio,
            "avisos": avisos,
            "armadura": {
                "As1_cm2": round(float(As1_m2 * 1e4), 4),
                "As1_min_cm2": round(float(As1_min_m2 * 1e4), 4),
                "As1_prov_cm2": round(float(As1_prov_m2 * 1e4), 4),
                "As2_cm2": round(float(As2_m2 * 1e4), 4),
            },
            "cisalhamento": {
                "theta_deg": theta_deg,
                "cot_theta": cot_theta,
                "Asw_s_req_cm2pm": round(float(Asw_s_req_m2pm) * 1e4, 4),
                "Asw_s_min_cm2pm": round(float(Asw_s_min_m2pm) * 1e4, 4),
                "Asw_s_prov_cm2pm": round(float(Asw_s_prov_m2pm) * 1e4, 4)},
            "pele": {
                "lim_h_pele_cm": lim_h_pele_m * 100,
                "As_pele_por_face_cm2": round(float(As_pele_por_face_m2 * 1e4), 4)},
            "flecha": {
                "flecha_imediata_cm": round(float(flecha_imediata_m) * 100, 4),
                "alpha_f": round(float(alpha_f), 4),
                "flecha_els_cm": round(float(flecha_els_m) * 100, 4),
                "flecha_lim_cm": round(float(flecha_lim_m) * 100, 4),
                "critério": f"L/{int(limite_flecha_L_sobre)}",
                "ok?": bool(flecha_ok)}
        }
    }

    return saida
