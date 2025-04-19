from project import Project, Section, Support, Load, Node
from config import SectionType, SupportType, LoadType

my_project = Project("Projeto X")
my_project.create_new()

my_project.section = Section(SectionType.R, {"b": 30, "h": 50})
my_project.section = Section(SectionType.R, None)

my_project.nodes.append(Node(0, Support(SupportType.Roller, 0)))
my_project.nodes.append(Node(5, Support(SupportType.Pinned, 0)))
my_project.nodes.append(Node(9, Support(SupportType.Fixed, 0)))
my_project.nodes.append(Node(12, None))

my_project.loads.append(Load(LoadType.M, [1], [5]))
my_project.loads.append(Load(LoadType.PL, [2], [-10]))
my_project.loads.append(Load(LoadType.UDL, [3, 4], [-5]))
my_project.loads.append(Load(LoadType.LVDL, [5, 6], [-5, -7]))

my_project.save_data()

print(my_project)
