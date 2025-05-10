from .BaseRepo import BaseRepo
from models.project import Project


class ProjectRepo(BaseRepo):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.set_collection("projects")

    async def create_project(self, project: Project):
        project_dict = project.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(project_dict)
        project.id = result.inserted_id
        return project

    async def get_or_create_project(self, project_id: str):
        project = await self.collection.find_one({"project_id": project_id})
        if project is None:
            _project = Project(project_id=project_id)
            return await self.create_project(_project)

        return Project(**project)

    async def get_all_projects(self, page: int = 1, limit: int = 10):
        curser = self.collection.find().skip((page - 1) * limit).limit(limit)
        projects = []
        async for project in curser:
            projects.append(Project(**project))

        return projects, len(projects)
