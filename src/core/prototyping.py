from Pynite import FEModel3D  # Import `FEModel3D` from `Pynite`

__all__ = ["start_prototype"]


def start_prototype():
    print("starting prototype...")

    # Create a new finite element model
    beam = FEModel3D()

    # Define the material
    E = 21e6  # Modulus of elasticity (Módulo de Elasticidade) (ksi) -> (kN/m²)
    # G = 7.9e6  # Shear modulus of elasticity (Módulo de Cisalhamento) (ksi) -> (kN/m²)
    G = 8.75e6  # Shear modulus of elasticity (Módulo de Cisalhamento) (ksi) -> (kN/m²)
    nu = 0.2  # Poisson's ratio (Coeficiente de Poisson)
    # rho = 23.544  # Density (Massa Específica) (kci) -> (kN/m³)
    rho = 25  # Density (Massa Específica) (kci) -> (kN/m³)

    print("")
    print("### Material Properties ###")
    material_name = "Concrete"

    res = input(f"Modulus of elasticity (E) [{E} kN/m²]: ")
    if res != "":
        E = float(res)
    res = input(f"Shear modulus of elasticity (G) [{G} kN/m²]: ")
    if res != "":
        G = float(res)
    res = input(f"Poisson's ratio (nu) [{nu}]: ")
    if res != "":
        nu = float(res)
    res = input(f"Density (rho) [{rho} kN/m³]: ")
    if res != "":
        rho = float(res)
    beam.add_material(material_name, E, G, nu, rho)

    # Add section properties:
    print("")
    print("### Section Properties ###")

    section_name = "Rectangle"
    A = 1_800  # cm^2
    Iy = 135_000  # cm^4
    Iz = 540_000  # cm^4
    J = 2_160_000  # cm^4

    res = input(f"Area (A) [{A} cm^2]: ")
    if res != "":
        A = float(res)
    res = input(f"Moment of Inertia around y-axis (Iy) [{Iy} cm^4]: ")
    if res != "":
        Iy = float(res)
    res = input(f"Moment of Inertia around z-axis (Iz) [{Iz} cm^4]: ")
    if res != "":
        Iz = float(res)
    res = input(f"The torsion constant of the section (J) [{J} cm^4]: ")
    if res != "":
        J = float(res)

    A /= 10e4
    Iy /= 10e8
    Iz /= 10e8
    J /= 10e8
    beam.add_section(section_name, A, Iy, Iz, J)

    # Add nodes
    print("")
    print("### Nodes ###")

    beam.add_node('N1', 0, 0, 0)
    node_order = ''
    while node_order not in ['0', '1', '2', '3']:
        node_order = input("N1 order: ")
    beam.def_support(f'N1', *get_order_booleans(node_order))
    print(f"added N1 [x=0m, order={node_order}]")

    node_cont = 1
    res = "a"
    while res != "":
        node_cont += 1
        res = input(f"N{node_cont} position [m]: ")
        if res != "":
            node_pos: float = float(res)
            beam.add_node(f"N{node_cont}", node_pos, 0, 0)

            node_order = 'a'
            while node_order not in ['0', '1', '2', '3']:
                node_order = input(f"N{node_cont} order: ")
            beam.def_support(f'N{node_cont}', *get_order_booleans(node_order))
            print(f"added N{node_cont} [x={node_pos} m, order={node_order}]")

    # Add members
    for i in range(1, len(beam.nodes)):
        beam.add_member(f'M{i}', f'N{i}', f'N{i + 1}', material_name, section_name)

    # Add loads
    res = 'a'
    while res not in ['y', 'n', '']:
        print("")
        res = input("add point load? [y/n]")
        if res in ['y', '']:
            member_name = input("member name: ")
            direction = input("direction [Fy/Mz]: ")
            P = float(input("P [kN]: "))
            x = float(input("x [m]: "))
            beam.add_member_pt_load(member_name, direction, P, x)
            res = 'a'

    res = 'a'
    while res not in ['y', 'n', '']:
        print("")
        res = input("add distributed load? [y/n]")
        if res in ['y', '']:
            member_name = input("member name: ")
            P0 = float(input("P0 [kN]: "))
            P1 = float(input("P1 [kN]: "))
            x0 = float(input("x0 [m]: "))
            x1 = float(input("x1 [m]: "))
            beam.add_member_dist_load(member_name, 'FY', P0, P1, x0, x1)
            res = 'a'

    # Alternatively the following line would do apply the load to the full
    # length of the member as well
    # beam.add_member_dist_load('M1', 'Fy', -5, -5)

    # Analyze the beam
    beam.analyze()

    print("")
    print("")
    print("##### RESULTS #####")

    # Print the shear, moment, and deflection diagrams
    for member_name, member in beam.members.items():
        member.plot_shear('Fy')
        member.plot_moment('Mz')
        member.plot_deflection('dy')

        # Print reactions at each end of the beam
        # print('Left Support Reaction:', beam.nodes['N1'].RxnFY["Combo 1"], 'kN')
        # print('Right Support Reacton:', beam.nodes['N2'].RxnFY["Combo 1"], 'kN')

        # print('Left Support Moment:', beam.nodes['N1'].RxnMZ["Combo 1"], 'kN.m')
        # print('Right Support Moment:', beam.nodes['N2'].RxnMZ["Combo 1"], 'kN.m')

        # deflections = member.deflection_array('dy', 3)
        # center_def = member.deflection('dy', 5)
        max_moment = member.max_moment('Mz')
        min_moment = member.min_moment('Mz')

        max_def = member.max_deflection('dy')
        min_def = member.min_deflection('dy')

        print(f"Member: {member_name}")
        print('Maximum Moment:', round(max_moment, 4), "kN.m")
        print('Minimum Moment:', round(min_moment, 4), "kN.m")
        print("")
        print('Maximum Deflection:', round(max_def, 4), "m")
        print('Minimum Deflection:', round(min_def, 4), "m")
        print("")
        print("")

    # Render the deformed shape of the beam magnified 100 times
    from Pynite.Visualization import Renderer

    renderer = Renderer(beam)
    renderer.annotation_size = 0.1
    renderer.deformed_shape = True
    renderer.deformed_scale = 1
    renderer.render_loads = True
    renderer.render_model()


def get_order_booleans(node_order) -> tuple[bool, bool, bool, bool, bool, bool]:
    match node_order:
        case "0":
            return False, False, True, True, True, False
        case "1":
            return False, True, True, True, True, False
        case "2":
            return True, True, True, True, True, False
        case "3":
            return True, True, True, True, True, True
