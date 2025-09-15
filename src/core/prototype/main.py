from core.prototype.dimensionamento import dimensionar_viga_ca
from tkinter import filedialog
from Pynite import FEModel3D
import math
import json

__all__ = ["start_prototype"]


def start_prototype():
    # region "DADOS DE ENTRADA"
    # --- Geometria da Seção
    b_m = .20  # base [m]
    h_m = .60  # altura [m]
    dp_m = .04  # distância As para bordo tracionado [m]
    # --- Materiais
    # concreto
    fck_MPa = 30.0  # fck [MPa]
    Ec_MPa = 25_000  # Módulo de Elasticidade [kN/m²]
    nu = 0.2  # Coeficiente de Poisson
    rho_c_kNm3 = 25  # Massa Específica [kN/m³]
    # aço
    fyk_MPa = 500.0  # fyk [MPa]
    Es_Mpa = 210_000.0  # Módulo de Elasticidade [MPa]
    # --- Parâmetros de cálculo (NBR 6118)
    j_date: int = 28  # data da verificação
    cimento: str = "CP II"  # tipo de cimento ("CP I", "CP II", "CP III", "CP IV" e "CP V-ARI")
    CAA: int = 2  # Classe de Agressividade Ambiental - NBR 6118:2023 Tabela 6.1
    cob: float | None = None  # cobrimento - NBR 6118:2023 Tabela 7.2
    gamma_c: float = 1.4
    gamma_s: float = 1.15
    gamma_f: float = 1.4  # coeficiente de majoração das ações
    alpha_c: float = 0.85  # fator tradicional do bloco retangular
    lambda_c: float = 0.8  # fator de profundidade do bloco (λ_c)
    # --- Cisalhamento (treliça de Mörsch)
    theta_deg: float = 45.0  # 30–45° usual
    # --- Armadura de pele (regra prática)
    lim_h_pele_m: float = 0.6  # exigir pele se h > 60 cm
    # --- Limites usuais
    rho_max: float = 0.04  # taxa de armadura ~ 4% (limite construtivo/funcional típico para vigas)
    # --- flecha diferida
    limite_flecha_L_sobre: float = 250.0  # verifica L/250 por padrão
    # endregion

    # region "DADOS CALCULADOS"
    d_m = h_m - dp_m  # distância As para bordo comprimido [m]

    A_m2 = b_m * h_m  # Área da seção transversal [m^2]
    Iy_m4 = h_m * (b_m ** 3) / 12  # Momento em torno do eixo y [m^4]
    Iz_m4 = b_m * (h_m ** 3) / 12  # Momento em torno do eixo z [m^4]
    J_m4 = b_m * (h_m ** 3) / 3  # Momento torsor [m^4]

    Ec_kNm2 = Ec_MPa * 1000  # Módulo de Elasticidade [kN/m²]
    Gc_kNm2 = Ec_kNm2 / 2.4  # Módulo de Cisalhamento [kN/m²]

    # cobrimento - NBR 6118:2023 Tabela 7.2
    if cob is None:
        if CAA == 1:
            cob = 2.5
        elif CAA == 2:
            cob = 3.0
        elif CAA == 3:
            cob = 4.0
        elif CAA == 4:
            cob = 5.0
        else:
            cob = 3.0
    # endregion

    example = 1
    print("iniciando protótipo...")
    print("exemplo:", example)

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

        beam.add_node('N2', 4, 0, 0)
        beam.def_support('N2', *get_order_booleans(1))

        beam.add_node('N3', 9, 0, 0)
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
        beam.add_member_pt_load('M1', 'Fy', -20, 3)
        beam.add_member_dist_load('M1', 'Fy', -10, -10, 0, 3)
        beam.add_member_dist_load('M1', 'Fy', -12, -12, 3, 6)
    elif example == 2:
        beam.add_member_pt_load('M1', 'Fy', -25, 2)
        beam.add_member_dist_load('M1', 'Fy', -12, -12)

        beam.add_member_pt_load('M2', 'Fy', -18, 2)
        beam.add_member_dist_load('M2', 'Fy', -12, -12, 0, 2)
        beam.add_member_dist_load('M2', 'Fy', -12, -15, 2, 5)
    elif example == 3:
        beam.add_member_dist_load('M1', 'Fy', -50, -50)

    # Analyze the beam
    beam.analyze()

    print("")
    print("Reações nos apoios:")
    for node_name, node in beam.nodes.items():
        print(node_name + ":")
        print("Fx:", round(node.RxnFX["Combo 1"], 4), 'kN')
        print("Fy:", round(node.RxnFY["Combo 1"], 4), 'kN')
        print("Mz:", round(node.RxnMZ["Combo 1"], 4), 'kN.m')
        print("")

    print("")
    for member_name, member in beam.members.items():
        # Plot the shear, moment, and deflection diagrams
        # member.plot_shear('Fy', n_points=10000)
        # member.plot_moment('Mz', n_points=10000)
        # member.plot_deflection('dy', n_points=10000)

        max_shear = member.max_shear('Fy')
        min_shear = member.min_shear('Fy')
        Vk_kNm = max(abs(max_shear), abs(min_shear))

        max_moment = member.max_moment('Mz')
        min_moment = member.min_moment('Mz')
        Mk_kNm = max(abs(max_moment), abs(min_moment))

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
                "M_min_kNm": round(min_moment, 4),
                "M_max_kNm": round(max_moment, 4),
                "Mk_kNm": round(Mk_kNm, 4),
                "dy_min_cm": round(min_def * 100, 4),
                "dy_max_cm": round(max_def * 100, 4),
                "flecha_imediata_cm": round(flecha_imediata_m * 100, 4)
            }
        }

        output_dimensionamento = dimensionar_viga_ca(
            bw_m=b_m, h_m=h_m, d_m=d_m, dp_m=dp_m, L_m=L_m,
            Vk_kN=Vk_kNm, Mk_kNm=Mk_kNm,
            fck_kNm2=fck_MPa * 1000.0, fyk_kNm2=fyk_MPa * 1000.0, Es_kNm2=Es_Mpa * 1000.0,
            j_date=j_date, cimento=cimento, CAA=CAA, cob=cob,
            gamma_c=gamma_c, gamma_s=gamma_s, gamma_f=gamma_f, alpha_c=alpha_c, lambda_c=lambda_c,
            theta_deg=theta_deg, lim_h_pele_m=lim_h_pele_m, rho_max=rho_max,
            flecha_imediata_m=flecha_imediata_m, limite_flecha_L_sobre=limite_flecha_L_sobre
        )

        output = {**output_isostatica, **output_dimensionamento}

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Json file", "*.json")],
            title="Choose file path to save"
        )

        json_str = json.dumps(output, indent=4, ensure_ascii=False)
        json_str_with_tabs = json_str.replace("    ", "\t")
        with open(file_path, "w", encoding="utf-8") as f:
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
