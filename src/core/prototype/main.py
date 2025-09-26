from core.prototype.dimensionamento import dimensionar_viga_ca
from tkinter import filedialog
from Pynite import FEModel3D
import math
import json

__all__ = ["start_prototype"]


def start_prototype():
    for fck_MPa in range(20, 91, 10):
        # region "DADOS DE ENTRADA"
        # --- Geometria da Seção
        b_m = .20  # base [m]
        h_m = .60  # altura [m]
        dp_m: float | None = None  # distância As para bordo tracionado [m]
        # --- Bitolas As e Asw
        phi_As_cm: float | None = 1.0  # bitola do As [cm]
        phi_Asw_cm: float | None = 0.8  # bitola do Asw [cm]
        # --- Materiais
        # concreto
        # fck_MPa: float = 30.0  # fck [MPa]
        Ec_MPa: float | None = None  # Módulo de Elasticidade [MPa] (ex: 25_000)
        Gc_MPa: float | None = None  # Módulo de Cisalhamento [MPa]
        nu = 0.2  # Coeficiente de Poisson
        rho_c_kNm3 = 25  # Massa Específica [kN/m³]
        # aço
        fyk_MPa = 500.0  # fyk [MPa]
        Es_Mpa = 210_000.0  # Módulo de Elasticidade [MPa]
        # --- Parâmetros de cálculo (NBR 6118)
        data_j: int = 28  # data da verificação
        cimento: str = "CP II"  # tipo do cimento ("CP I", "CP II", "CP III", "CP IV" e "CP V-ARI")
        alpha_E: float = 1.0  # fator do agregado graúdo (0.7, 0.9, 1.0 e 1.2) - NBR 6118:2023 Item 8.2.8
        CAA: int = 2  # Classe de Agressividade Ambiental (CAA) - NBR 6118:2023 Tabela 6.1
        cob_cm: float | None = None  # cobrimento [cm] - NBR 6118:2023 Tabela 7.2
        gamma_c: float = 1.4
        gamma_s: float = 1.15
        gamma_f: float = 1.4  # coeficiente de majoração das ações
        alpha_c: float | None = None  # fator tradicional do bloco retangular
        lambda_c: float | None = None  # fator de profundidade do bloco (λ_c)
        # --- Cisalhamento (treliça de Mörsch)
        theta_deg: float = 45.0  # 30–45° usual
        alpha_deg: float = 90.0  # 90° usual (estribo vertical)
        # --- Armadura de pele (regra prática)
        lim_h_pele_m: float = 0.6  # exigir pele se h > 60 cm
        # --- flecha diferida
        limite_flecha_L_sobre: float = 250.0  # verifica L/250 por padrão
        # endregion

        # region "DADOS CALCULADOS"
        # cobrimento - NBR 6118:2023 Tabela 7.2
        if cob_cm is None:
            if CAA == 1:
                cob_cm = 2.5
            elif CAA == 2:
                cob_cm = 3.0
            elif CAA == 3:
                cob_cm = 4.0
            elif CAA == 4:
                cob_cm = 5.0
            else:
                cob_cm = 3.0

        if dp_m is None:
            dp_m = (cob_cm + phi_Asw_cm + phi_As_cm / 2) / 100
        d_m = h_m - dp_m  # distância As para bordo comprimido [m]

        A_m2 = b_m * h_m  # Área da seção transversal [m^2]
        Iy_m4 = h_m * (b_m ** 3) / 12  # Momento em torno do eixo y [m^4]
        Iz_m4 = b_m * (h_m ** 3) / 12  # Momento em torno do eixo z [m^4]
        J_m4 = b_m * (h_m ** 3) / 3  # Momento torsor [m^4]

        # Módulo de Elasticidade
        if Ec_MPa is None:
            if fck_MPa <= 50:
                Ec_MPa = alpha_E * 5_600 * math.sqrt(fck_MPa)
            else:
                Ec_MPa = alpha_E * 21_500 * ((fck_MPa / 10) + 1.25) ** (1 / 3)
        if Gc_MPa is None:
            Gc_MPa = Ec_MPa / 2.4
        Ec_kNm2 = Ec_MPa * 1e3  # Módulo de Elasticidade [kN/m²]
        Gc_kNm2 = Gc_MPa * 1e3  # Módulo de Cisalhamento [kN/m²]

        if alpha_c is None:
            if fck_MPa <= 50:
                alpha_c = 0.85
            else:
                alpha_c = 0.85 * (1 - (fck_MPa - 50) / 200)
        if lambda_c is None:
            if fck_MPa <= 50:
                lambda_c = 0.8
            else:
                lambda_c = 0.8 - (fck_MPa - 50) / 400
        # endregion

        example = 1
        # print("iniciando protótipo...")
        # print("exemplo:", example)

        # Create a new finite element model
        beam = FEModel3D()

        # Define the material
        material_name = "Concrete"
        beam.add_material(material_name, Ec_kNm2, Gc_kNm2, nu, rho_c_kNm3)

        # Add section properties:
        section_name = "Rectangle"
        beam.add_section(section_name, A_m2, Iy_m4, Iz_m4, J_m4)

        # Add nodes
        if example == 1:
            beam.add_node('N1', 0, 0, 0)
            beam.def_support('N1', *get_order_booleans(1))

            beam.add_node('N2', 6, 0, 0)
            beam.def_support('N2', *get_order_booleans(2))
        elif example == 2:
            beam.add_node('N1', 0, 0, 0)
            beam.def_support('N1', *get_order_booleans(2))

            beam.add_node('N2', 5, 0, 0)
            beam.def_support('N2', *get_order_booleans(1))

            beam.add_node('N3', 11, 0, 0)
            beam.def_support('N3', *get_order_booleans(2))
        elif example == 3:
            beam.add_node('N1', 0, 0, 0)
            beam.def_support('N1', *get_order_booleans(1))

            beam.add_node('N2', 10, 0, 0)
            beam.def_support('N2', *get_order_booleans(2))

        # Add members
        for i in range(1, len(beam.nodes)):
            beam.add_member(f'M{i}', f'N{i}', f'N{i + 1}', material_name, section_name)

        # Add loads
        if example == 1:
            # beam.add_member_pt_load('M1', 'Fy', -20, 3)
            # beam.add_member_dist_load('M1', 'Fy', -15, -15, 0, 3)
            # beam.add_member_dist_load('M1', 'Fy', -18, -18, 3, 6)
            beam.add_member_pt_load('M1', 'Fy', -30, 3)
            beam.add_member_dist_load('M1', 'Fy', -50, -50, 0, 3)
            beam.add_member_dist_load('M1', 'Fy', -70, -70, 3, 6)
        elif example == 2:
            beam.add_member_pt_load('M1', 'Fy', -30, 2.5)
            beam.add_member_dist_load('M1', 'Fy', -25, -25)

            beam.add_member_pt_load('M2', 'Fy', -35, 2)
            beam.add_member_dist_load('M2', 'Fy', -25, -25, 0, 2)
            beam.add_member_dist_load('M2', 'Fy', -25, -35, 2, 6)
        elif example == 3:
            # beam.add_member_dist_load('M1', 'Fy', -100, -100)
            beam.add_member_pt_load('M1', 'Fy', -10, 5)

        # Analyze the beam
        beam.analyze()

        # print("")
        # print("Reações nos apoios:")
        # for node_name, node in beam.nodes.items():
        #     print(node_name + ":")
        #     print("Fx:", round(node.RxnFX["Combo 1"], 4), 'kN')
        #     print("Fy:", round(node.RxnFY["Combo 1"], 4), 'kN')
        #     print("Mz:", round(node.RxnMZ["Combo 1"], 4), 'kN.m')
        #     print("")

        # print("")
        for member_name, member in beam.members.items():
            # Plot the shear, moment, and deflection diagrams
            # member.plot_shear('Fy', n_points=10000)
            # member.plot_moment('Mz', n_points=10000)
            # member.plot_deflection('dy', n_points=10000)

            max_shear = member.max_shear('Fy')
            min_shear = member.min_shear('Fy')
            Vk_kNm = max(abs(max_shear), abs(min_shear))

            Mk_neg_kNm = abs(member.max_moment('Mz'))
            Mk_pos_kNm = abs(member.min_moment('Mz'))

            max_def = member.max_deflection('dy')
            min_def = member.min_deflection('dy')
            flecha_imediata_m = max(abs(max_def), abs(min_def))

            L_m = math.sqrt(
                (member.j_node.X - member.i_node.X) ** 2 +
                (member.j_node.Y - member.i_node.Y) ** 2 +
                (member.j_node.Z - member.i_node.Z) ** 2
            )

            output_isostatica = {
                "sol_int": {
                    "N_esq": {
                        "Fx_kN": round(member.i_node.RxnFX["Combo 1"], 4),
                        "Fy_kN": round(member.i_node.RxnFY["Combo 1"], 4),
                        "Mz_kNm": round(member.i_node.RxnMZ["Combo 1"], 4)
                    },
                    "N_dir": {
                        "Fx_kN": round(member.j_node.RxnFX["Combo 1"], 4),
                        "Fy_kN": round(member.j_node.RxnFY["Combo 1"], 4),
                        "Mz_kNm": round(member.j_node.RxnMZ["Combo 1"], 4)
                    },
                    "Q_min_kN": round(min_shear, 4),
                    "Q_max_kN": round(max_shear, 4),
                    "Vk_kN": round(Vk_kNm, 4),
                    "Mk_pos_kNm": round(Mk_pos_kNm, 4),
                    "Mk_neg_kNm": round(Mk_neg_kNm, 4),
                    "dy_min_cm": round(min_def * 100, 4),
                    "dy_max_cm": round(max_def * 100, 4),
                    "flecha_imediata_cm": round(flecha_imediata_m * 100, 4)
                }
            }

            if Mk_pos_kNm > 1e-9:
                output_dimensionamento_pos = dimensionar_viga_ca(
                    bw_m=b_m, h_m=h_m, d_m=d_m, dp_m=dp_m, L_m=L_m,
                    Vk_kN=Vk_kNm, Mk_kNm=Mk_pos_kNm,
                    fck_MPa=fck_MPa, fyk_MPa=fyk_MPa, Ec_MPa=Ec_MPa, Es_MPa=Es_Mpa,
                    data_j=data_j, cimento=cimento, alpha_E=alpha_E, CAA=CAA, cob_cm=cob_cm,
                    gamma_c=gamma_c, gamma_s=gamma_s, gamma_f=gamma_f, alpha_c=alpha_c, lambda_c=lambda_c,
                    theta_deg=theta_deg, alpha_deg=alpha_deg, lim_h_pele_m=lim_h_pele_m,
                    flecha_imediata_m=flecha_imediata_m, limite_flecha_L_sobre=limite_flecha_L_sobre
                )
                output_pos = {**output_isostatica, **output_dimensionamento_pos}

                # print(f"{output_pos['dados']['xi']}\t"
                #       f"{output_pos['dados']['mu']}\t"
                #       f"{output_pos['dados']['mu_lim']}\t"
                #       f"{output_pos['dimensionamento']['armadura']['longitudinal']['As1_prov_cm2']}\t"
                #       f"{output_pos['dimensionamento']['armadura']['longitudinal']['As2_cm2']}\t"
                #       f"{output_pos['dimensionamento']['armadura']['cisalhamento']['Asw_s_prov_cm2pm']}\t"
                #       f"{output_pos['dimensionamento']['flecha']['flecha_els_cm']}")

                print(f"{fck_MPa}\t"
                      f"{output_pos['dimensionamento']['flecha']['flecha_imediata_cm']}\t"
                      f"{output_pos['dimensionamento']['flecha']['flecha_els_cm']}")

                # file_path_pos = filedialog.asksaveasfilename(
                #     initialfile=f"ex{example}_{member_name}_pos_fck{fck_MPa}",
                #     defaultextension=".json",
                #     filetypes=[("Json file", "*.json")],
                #     title="Choose file path to save (POSITIVE)"
                # )
                # if file_path_pos:
                #     json_str = json.dumps(output_pos, indent=4, ensure_ascii=False)
                #     json_str_with_tabs = json_str.replace("    ", "\t")
                #     with open(file_path_pos, "w", encoding="utf-8") as f:
                #         f.write(json_str_with_tabs)

            if Mk_neg_kNm > 1e-9:
                output_dimensionamento_neg = dimensionar_viga_ca(
                    bw_m=b_m, h_m=h_m, d_m=d_m, dp_m=dp_m, L_m=L_m,
                    Vk_kN=Vk_kNm, Mk_kNm=Mk_neg_kNm,
                    fck_MPa=fck_MPa, fyk_MPa=fyk_MPa, Ec_MPa=Ec_MPa, Es_MPa=Es_Mpa,
                    data_j=data_j, cimento=cimento, alpha_E=alpha_E, CAA=CAA, cob_cm=cob_cm,
                    gamma_c=gamma_c, gamma_s=gamma_s, gamma_f=gamma_f, alpha_c=alpha_c, lambda_c=lambda_c,
                    theta_deg=theta_deg, alpha_deg=alpha_deg, lim_h_pele_m=lim_h_pele_m,
                    flecha_imediata_m=flecha_imediata_m, limite_flecha_L_sobre=limite_flecha_L_sobre
                )
                output_neg = {**output_isostatica, **output_dimensionamento_neg}

                file_path_neg = filedialog.asksaveasfilename(
                    initialfile=f"ex{example}_{member_name}_neg",
                    defaultextension=".json",
                    filetypes=[("Json file", "*.json")],
                    title="Choose file path to save (NEGATIVE)"
                )
                if file_path_neg:
                    json_str = json.dumps(output_neg, indent=4, ensure_ascii=False)
                    json_str_with_tabs = json_str.replace("    ", "\t")
                    with open(file_path_neg, "w", encoding="utf-8") as f:
                        f.write(json_str_with_tabs)


def get_order_booleans(node_order) -> tuple[bool, bool, bool, bool, bool, bool]:
    match node_order:
        case 0:
            return False, False, True, True, True, False
        case 1:
            return False, True, True, True, True, False
        case 2:
            return True, True, True, True, True, False
        case 3:
            return True, True, True, True, True, True
