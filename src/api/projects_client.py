from src.api.base_client import BaseAPIClient


class ProjectsClient(BaseAPIClient):
    def create_project(self, name: str, description: str = "", team_members=None) -> dict:
        resp = self.post(
            "/projects",
            json={
                "name": name,
                "description": description,
                "team_members": team_members or [],
            },
        )
        # ASSUMPTION: spec only gave the response body, not the status code --
        # assuming REST convention (201 Created) for a successful POST.
        assert resp.status_code == 201, f"Project creation failed: {resp.status_code} {resp.text}"
        return resp.json()

    def get_project(self, project_id: int):
        return self.get(f"/projects/{project_id}")

    def delete_project(self, project_id: int):
        return self.delete(f"/projects/{project_id}")
