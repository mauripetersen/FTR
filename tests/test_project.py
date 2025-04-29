from project import Project, Section, Support, Node, Load, PLLoad, DLLoad
from config import SectionType, SupportType, LoadType

my_project = Project("Projeto X")
my_project.create()

my_project.section = Section(SectionType.R, {"b": 30, "h": 50})
my_project.section = Section(SectionType.R, None)

my_project.nodes.append(Node(0, Support(SupportType.Roller, 0)))
my_project.nodes.append(Node(5, Support(SupportType.Pinned, 0)))
my_project.nodes.append(Node(9, Support(SupportType.Fixed, 0)))
my_project.nodes.append(Node(12, None))

my_project.loads.append(PLLoad(position=2.5, fx=0.0, fy=0.0, mz=5.0))
my_project.loads.append(PLLoad(position=5.0, fx=0.0, fy=0.0, mz=-5.0))
my_project.loads.append(DLLoad(start=0.0, end=0.0, q_start=0.0, q_end=0.0))

my_project.save_data()

print(my_project)
