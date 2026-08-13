# Test Plan — WorkFlow Pro QA Automation

Condensed scenario coverage across authentication, API, web UI, mobile,
tenant security, and role permissions. Full reasoning behind each area is in
the case-study response document.

| Test Area        | Scenario                                         | Expected Result                                              | Automated In |
|-------------------|---------------------------------------------------|----------------------------------------------------------------|--------------|
| Authentication    | Valid credentials, no 2FA                          | Redirected to dashboard, welcome message visible               | `tests/ui/test_login.py` |
| Authentication    | Valid credentials, 2FA-enabled account             | OTP step presented and handled before dashboard loads          | `tests/ui/test_login.py` |
| Authentication    | Invalid password                                   | Clear error shown, no navigation to dashboard                  | `tests/ui/test_login.py` |
| Multi-Tenant UI   | User views project list                            | Only that tenant's projects shown, none from other tenants     | `tests/ui/test_login.py` |
| Projects API      | `POST /api/v1/projects` with valid payload         | 201 response, project object returned with an `id`             | `tests/api/test_projects_api.py` |
| Projects API      | `GET /api/v1/projects/{id}` as owning tenant       | 200 response with correct project data                         | `tests/api/test_projects_api.py` |
| Projects API      | `GET /api/v1/projects/{id}` as a different tenant  | 403/404, not project data                                      | `tests/api/test_projects_api.py` |
| Web UI            | Newly created project appears in project list      | Project card visible with correct name                         | `tests/integration/test_project_creation_flow.py` |
| Mobile            | Project accessible from mobile view/app            | Project visible and correctly rendered on target device        | `tests/integration/test_project_creation_flow.py`, `tests/mobile/test_mobile_access.py` |
| Tenant Security   | Company B requests Company A's project by ID       | 403/404, not project data                                      | `tests/integration/test_project_creation_flow.py` |
| Tenant Security   | Company B browses project list                     | Company A's project never appears, even by name search         | `tests/integration/test_project_creation_flow.py` |
| Roles             | Employee attempts a Manager/Admin-only action      | Action blocked / control not shown, per `config/roles.yaml`     | `tests/ui/test_project_management.py` |
| Roles             | Manager can invite team members, Employee cannot   | UI control hidden or API call rejected for Employee role       | `tests/ui/test_project_management.py` |

## Out of Scope / Needs Clarification

- Native iOS/Android app testing (assumed mobile web for now — see Assumptions
  in the case-study doc).
- Password-reset and account-lockout flows (not mentioned in the case study).
- Load/performance testing.
- Data-privacy handling of any production-like test data.

## Environments Covered

- `company1` (staging tenant, Admin/Manager/Employee test accounts)
- `company2` (staging tenant, used for isolation checks)
- `staging` (shared, non-tenant-specific smoke checks)
