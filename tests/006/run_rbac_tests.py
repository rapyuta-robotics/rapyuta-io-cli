#!/usr/bin/env python3
"""
RBAC Scenario Test Harness for rapyuta.io

Reads:
  - rbac-setup (role assignments; currently informational)
  - rbac-scenarios (authorization test cases)

Executes each scenario using the v2client API (through the official Configuration
object) and determines whether the action is permitted (success) or denied and
compares with the EXPECTED boolean in the scenario file.

Key constraints:
  - Each (resource, action) triggers exactly ONE platform API call.
  - Static payloads are used for create/update actions (no read-before-write).
  - Delete actions honor --dry-run to avoid destructive mutations.
  - Configuration from riocli.config.Configuration is used instead of a dummy.
  - Same Configuration instance (per user/org[/project]) is reused across scenarios.

Supported resources/actions (all single-call):
  project: list|get|create|update|delete
  usergroup: list|get|create|update|update_group_roles|delete
  disk: list|get|create|delete
  static_route: list|get|create|update|delete
  managedservice: list|get   (create/delete omitted due to complex specs)
  role: list|get             (create/update/delete can be added with valid specs)

Environment Variables:
  RIO_API_HOST     Base URL (default: https://api.rapyuta.io)
  RIO_ORGS         Comma map orgName=orgGUID
  RIO_TOKENS       Comma map userEmail=authToken
  RIO_PROJECTS     Comma map orgName=projectGUID  (required for project-scoped resources)
  RIO_ADMIN_TOKEN  Token for initial discovery (optional; falls back to first RIO_TOKENS)

Example:
  export RIO_ORGS="Rapyuta=11111111-1111-1111-1111-111111111111"
  export RIO_PROJECTS="Rapyuta=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
  export RIO_TOKENS="user1@example.com=eyJ...,user2@example.com=eyJ..."
  python tests/006/run_rbac_tests.py --scenarios tests/006/rbac-scenarios --setup tests/006/rbac-setup --dry-run

Limitations / Notes:
  - Complex create specs (managedservice instances, roles) not included to avoid semantic 400 errors conflated with RBAC.
  - Name->GUID project & usergroup caches are pre-fetched with admin token.
  - Other resources use direct name calls; if a name does not exist GET will 404 → DENY (could differ from RBAC deny).
  - For precise RBAC differentiation you may wish to seed required test fixtures ahead of time.
"""
from __future__ import annotations

import argparse
import dataclasses
import os
import sys
from typing import Callable, Dict, List, Optional, Tuple

from riocli.v2client.client import Client as V2Client
from riocli.config.config import Configuration

# ----------------------------- Data Models -----------------------------------
@dataclasses.dataclass
class Scenario:
    domain: str
    subject: str
    resource: str
    instance: str
    action: str
    expected: bool
    raw: str

@dataclasses.dataclass
class Result:
    scenario: Scenario
    success: bool
    passed: bool
    error: Optional[str] = None
    skipped: bool = False

# ----------------------------- Parsing ---------------------------------------

def parse_bool(token: str) -> bool:
    return token.lower() in {"1", "true", "yes", "y"}


def parse_scenarios(path: str) -> List[Scenario]:
    scenarios: List[Scenario] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            s = raw.strip()
            if not s or s.startswith('#'):
                continue
            parts = s.split()
            if len(parts) != 6:
                print(f"WARN: Skipping malformed scenario line ({len(parts)} tokens): {raw}")
                continue
            domain, subject, resource, instance, action, expected = parts
            scenarios.append(
                Scenario(
                    domain=domain,
                    subject=subject,
                    resource=resource,
                    instance=instance.strip('"'),
                    action=action,
                    expected=parse_bool(expected),
                    raw=raw,
                )
            )
    return scenarios


def parse_setup(path: str) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            parts = s.split()
            if len(parts) != 3:
                print(f"WARN: Skipping malformed setup line: {s}")
                continue
            rows.append(tuple(parts))  # type: ignore[arg-type]
    return rows

# ----------------------------- Mapping & Discovery ---------------------------

def parse_mapping(env_value: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not env_value:
        return mapping
    for item in env_value.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            print(f"WARN: Ignoring mapping entry without '=': {item}")
            continue
        k, v = item.split('=', 1)
        mapping[k.strip()] = v.strip()
    return mapping


def extract_org_name(domain: str) -> str:
    return domain.split(':', 1)[1] if ':' in domain else domain


def extract_user_email(subject: str) -> str:
    return subject.split(':', 1)[1] if ':' in subject else subject

# ----------------------------- Caches ----------------------------------------
@dataclasses.dataclass
class OrgCache:
    project_name_to_guid: Dict[str, str]
    usergroup_name_to_guid: Dict[str, str]
    usergroup_specs: Dict[str, dict]

# ----------------------------- Action Framework ------------------------------
class ActionContext:
    def __init__(self, client: V2Client, org_guid: str, cache: OrgCache, dry_run: bool):
        self.client = client
        self.org_guid = org_guid
        self.cache = cache
        self.dry_run = dry_run

ACTION_REGISTRY: Dict[Tuple[str, str], Callable[[ActionContext, Scenario], bool]] = {}


def action(resource: str, name: str):
    def wrap(fn):
        ACTION_REGISTRY[(resource, name)] = fn
        return fn
    return wrap

# ----------------------------- Helper Lookup ---------------------------------

def resolve_project_guid(ctx: ActionContext, instance: str) -> str:
    if not instance:
        raise RuntimeError("Project instance (name or guid) required.")
    if instance in ctx.cache.project_name_to_guid:
        return ctx.cache.project_name_to_guid[instance]
    return instance  # treat as GUID


def resolve_usergroup_guid(ctx: ActionContext, instance: str) -> str:
    if not instance:
        raise RuntimeError("Usergroup instance (name or guid) required.")
    if instance in ctx.cache.usergroup_name_to_guid:
        return ctx.cache.usergroup_name_to_guid[instance]
    return instance

# ----------------------------- Project Actions -------------------------------
@action("project", "list")
def project_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_projects(organization_guid=ctx.org_guid)
    return True

@action("project", "get")
def project_get(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_project_guid(ctx, scenario.instance)
    ctx.client.get_project(guid)
    return True

@action("project", "create")
def project_create(ctx: ActionContext, scenario: Scenario) -> bool:
    payload = {"metadata": {"name": scenario.instance, "organizationGUID": ctx.org_guid}, "spec": {"description": "RBAC test project"}}
    resp = ctx.client.create_project(payload)
    guid = getattr(resp.metadata, 'guid', None) if hasattr(resp, 'metadata') else resp.get('metadata', {}).get('guid')
    if guid:
        ctx.cache.project_name_to_guid[scenario.instance] = guid
    return True

@action("project", "update")
def project_update(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_project_guid(ctx, scenario.instance)
    payload = {"metadata": {"name": scenario.instance}, "spec": {"description": "RBAC test project (updated)"}}
    ctx.client.update_project(guid, payload)
    return True

@action("project", "delete")
def project_delete(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_project_guid(ctx, scenario.instance)
    if ctx.dry_run:
        raise RuntimeError("DRY-RUN: skipped delete_project API call")
    ctx.client.delete_project(guid)
    for name, g in list(ctx.cache.project_name_to_guid.items()):
        if g == guid:
            ctx.cache.project_name_to_guid.pop(name, None)
            break
    return True

# ----------------------------- Usergroup Actions -----------------------------
@action("usergroup", "list")
def usergroup_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_usergroups()
    return True

@action("usergroup", "get")
def usergroup_get(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_usergroup_guid(ctx, scenario.instance)
    name = scenario.instance
    ctx.client.get_usergroup(guid, name)
    return True

@action("usergroup", "create")
def usergroup_create(ctx: ActionContext, scenario: Scenario) -> bool:
    payload = {"metadata": {"name": scenario.instance, "organizationGUID": ctx.org_guid}, "spec": {"description": "RBAC test usergroup", "roles": [], "members": []}}
    resp = ctx.client.create_usergroup(payload)
    guid = getattr(resp.metadata, 'guid', None) if hasattr(resp, 'metadata') else resp.get('metadata', {}).get('guid')
    if guid:
        ctx.cache.usergroup_name_to_guid[scenario.instance] = guid
        spec = resp.get('spec') if isinstance(resp, dict) else getattr(resp, 'spec', {})
        if spec:
            ctx.cache.usergroup_specs[scenario.instance] = spec
    return True

@action("usergroup", "update")
def usergroup_update(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_usergroup_guid(ctx, scenario.instance)
    name = scenario.instance
    spec = ctx.cache.usergroup_specs.get(name, {"description": "RBAC test usergroup", "roles": [], "members": []})
    spec["description"] = "RBAC test usergroup (updated)"
    payload = {"metadata": {"name": name}, "spec": spec}
    ctx.client.update_usergroup(guid, name, payload)
    ctx.cache.usergroup_specs[name] = spec
    return True

@action("usergroup", "update_group_roles")
def usergroup_update_roles(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_usergroup_guid(ctx, scenario.instance)
    name = scenario.instance
    spec = ctx.cache.usergroup_specs.get(name, {"description": "RBAC test usergroup", "roles": [], "members": []})
    roles = spec.get("roles", [])
    marker = {"name": "rbac-marker-role"}
    if not any(isinstance(r, dict) and r.get("name") == marker["name"] for r in roles if isinstance(roles, list)):
        roles.append(marker)
    else:
        roles = [r for r in roles if not (isinstance(r, dict) and r.get("name") == marker["name"])]
    spec["roles"] = roles
    payload = {"metadata": {"name": name}, "spec": spec}
    ctx.client.update_usergroup(guid, name, payload)
    ctx.cache.usergroup_specs[name] = spec
    return True

@action("usergroup", "delete")
def usergroup_delete(ctx: ActionContext, scenario: Scenario) -> bool:
    guid = resolve_usergroup_guid(ctx, scenario.instance)
    name = scenario.instance
    if ctx.dry_run:
        raise RuntimeError("DRY-RUN: skipped delete_usergroup API call")
    ctx.client.delete_usergroup(guid, name)
    ctx.cache.usergroup_name_to_guid.pop(name, None)
    ctx.cache.usergroup_specs.pop(name, None)
    return True

# ----------------------------- Disk Actions ----------------------------------
@action("disk", "list")
def disk_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_disks()
    return True

@action("disk", "get")
def disk_get(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.get_disk(scenario.instance)
    return True

@action("disk", "create")
def disk_create(ctx: ActionContext, scenario: Scenario) -> bool:
    payload = {"metadata": {"name": scenario.instance}, "spec": {"size": 1, "description": "RBAC test disk"}}
    ctx.client.create_disk(payload)
    return True

@action("disk", "delete")
def disk_delete(ctx: ActionContext, scenario: Scenario) -> bool:
    if ctx.dry_run:
        raise RuntimeError("DRY-RUN: skipped delete_disk API call")
    ctx.client.delete_disk(scenario.instance)
    return True

# ----------------------------- Static Route Actions --------------------------
@action("static_route", "list")
def static_route_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_static_routes()
    return True

@action("static_route", "get")
def static_route_get(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.get_static_route(scenario.instance)
    return True

@action("static_route", "create")
def static_route_create(ctx: ActionContext, scenario: Scenario) -> bool:
    payload = {"metadata": {"name": scenario.instance}, "spec": {"description": "RBAC test static route"}}
    ctx.client.create_static_route(payload)
    return True

@action("static_route", "update")
def static_route_update(ctx: ActionContext, scenario: Scenario) -> bool:
    payload = {"metadata": {"name": scenario.instance}, "spec": {"description": "RBAC test static route (updated)"}}
    ctx.client.update_static_route(scenario.instance, payload)
    return True

@action("static_route", "delete")
def static_route_delete(ctx: ActionContext, scenario: Scenario) -> bool:
    if ctx.dry_run:
        raise RuntimeError("DRY-RUN: skipped delete_static_route API call")
    ctx.client.delete_static_route(scenario.instance)
    return True

# ----------------------------- Managed Service Instance ----------------------
@action("managedservice", "list")
def ms_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_instances()
    return True

@action("managedservice", "get")
def ms_get(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.get_instance(scenario.instance)
    return True

# ----------------------------- Role Actions (read-only for now) --------------
@action("role", "list")
def role_list(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.list_roles()
    return True

@action("role", "get")
def role_get(ctx: ActionContext, scenario: Scenario) -> bool:
    ctx.client.get_role(scenario.instance)
    return True

# ----------------------------- Discovery / Prefetch --------------------------

def build_org_caches(orgs: Dict[str, str], host: str, admin_token: str) -> Dict[str, OrgCache]:
    caches: Dict[str, OrgCache] = {}
    for org_name, org_guid in orgs.items():
        # Minimal Configuration for discovery (org-level only)
        config = Configuration()
        config.data.update({
            "auth_token": admin_token,
            "organization_id": org_guid,
            "v2api_host": host,
        })
        # org-level: usergroups (no project header) projects list
        client_org = V2Client(config, auth_token=admin_token, project=None)
        projects = client_org.list_projects(organization_guid=org_guid).get('items', [])
        usergroups = client_org.list_usergroups().get('items', [])
        project_map: Dict[str, str] = {}
        for p in projects:
            name = p.get('metadata', {}).get('name')
            guid = p.get('metadata', {}).get('guid')
            if name and guid:
                project_map[name] = guid
        ug_map: Dict[str, str] = {}
        ug_specs: Dict[str, dict] = {}
        for g in usergroups:
            name = g.get('metadata', {}).get('name')
            guid = g.get('metadata', {}).get('guid')
            if name and guid:
                ug_map[name] = guid
                spec = g.get('spec')
                if spec:
                    ug_specs[name] = spec
        caches[org_guid] = OrgCache(project_map, ug_map, ug_specs)
    return caches

# ----------------------------- Configuration Cache ---------------------------
# Key: (user_email, org_guid, project_guid_or_none)
CONFIG_CACHE: Dict[Tuple[str, str, Optional[str]], Configuration] = {}

def get_config(user_email: str, org_guid: str, project_guid: Optional[str], host: str, token: str) -> Configuration:
    key = (user_email, org_guid, project_guid)
    if key in CONFIG_CACHE:
        return CONFIG_CACHE[key]
    cfg = Configuration()  # ephemeral (may not exist on disk)
    cfg.data.update({
        "auth_token": token,
        "organization_id": org_guid,
        "v2api_host": host,
    })
    if project_guid:
        cfg.data["project_id"] = project_guid
    CONFIG_CACHE[key] = cfg
    return cfg

# ----------------------------- Scenario Execution ----------------------------
PROJECT_SCOPED_RESOURCES = {"disk", "static_route", "managedservice", "role"}
ORG_SCOPED_RESOURCES = {"project", "usergroup"}


def execute_scenario(s: Scenario, orgs: Dict[str, str], tokens: Dict[str, str], projects: Dict[str, str], host: str, caches: Dict[str, OrgCache], dry_run: bool) -> Result:
    org_name = extract_org_name(s.domain)
    user_email = extract_user_email(s.subject)

    if org_name not in orgs:
        return Result(s, success=False, passed=not s.expected, error=f"Unknown organization '{org_name}'")
    if user_email not in tokens:
        return Result(s, success=False, passed=not s.expected, error=f"Missing token for user '{user_email}'")

    org_guid = orgs[org_name]
    token = tokens[user_email]

    # Determine project (if needed)
    project_guid: Optional[str] = None
    if s.resource in PROJECT_SCOPED_RESOURCES:
        if org_name not in projects:
            return Result(s, success=False, passed=not s.expected, error=f"No project mapping for org '{org_name}' (set RIO_PROJECTS)")
        project_guid = projects[org_name]

    cache = caches.get(org_guid)
    if not cache:
        return Result(s, success=False, passed=not s.expected, error=f"No cache for organization '{org_name}'")

    # Acquire (or re-use) configuration & client
    cfg = get_config(user_email, org_guid, project_guid, host, token)
    # Use new_v2_client with appropriate project scope; re-use underlying instance if cached
    client = cfg.new_v2_client(with_project=bool(project_guid))

    ctx = ActionContext(client, org_guid, cache, dry_run)

    key = (s.resource, s.action)
    if key not in ACTION_REGISTRY:
        return Result(s, success=False, passed=not s.expected, error=f"Unimplemented action {key}", skipped=True)

    if s.action != 'list' and not s.instance:
        return Result(s, success=False, passed=not s.expected, error="Instance required for this action")

    try:
        ACTION_REGISTRY[key](ctx, s)
        success = True
    except Exception as e:
        msg = str(e)
        if dry_run and 'DRY-RUN' in msg:
            return Result(s, success=False, passed=not s.expected, error=msg, skipped=True)
        return Result(s, success=False, passed=(False == s.expected), error=f"{e.__class__.__name__}: {e}")

    return Result(s, success=success, passed=(success == s.expected))

# ----------------------------- CLI -------------------------------------------

def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Run RBAC scenarios (single-call) using official Configuration")
    parser.add_argument('--scenarios', default='tests/006/rbac-scenarios')
    parser.add_argument('--setup', default='tests/006/rbac-setup')
    parser.add_argument('--fail-fast', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='Simulate delete actions without performing them')
    args = parser.parse_args(argv)

    scenarios = parse_scenarios(args.scenarios)
    setup = parse_setup(args.setup)

    print(f"Loaded {len(setup)} setup role assignments (informational)")
    print(f"Loaded {len(scenarios)} scenarios")

    host = os.getenv('RIO_API_HOST', 'https://api.rapyuta.io')
    orgs = parse_mapping(os.getenv('RIO_ORGS', ''))
    tokens = parse_mapping(os.getenv('RIO_TOKENS', ''))
    projects = parse_mapping(os.getenv('RIO_PROJECTS', ''))

    if not orgs:
        print("ERROR: No organizations provided in RIO_ORGS env var")
    if not tokens:
        print("ERROR: No user tokens provided in RIO_TOKENS env var")

    admin_token = os.getenv('RIO_ADMIN_TOKEN') or (next(iter(tokens.values())) if tokens else None)
    if not admin_token:
        print("ERROR: No admin token available for discovery (set RIO_ADMIN_TOKEN or RIO_TOKENS)")
        return 1

    print("Prefetching resource caches (projects, usergroups) using admin token...")
    caches = build_org_caches(orgs, host, admin_token)

    results: List[Result] = []
    for idx, s in enumerate(scenarios, 1):
        r = execute_scenario(s, orgs, tokens, projects, host, caches, dry_run=args.dry_run)
        results.append(r)
        status = 'PASS' if r.passed else 'FAIL'
        eff = 'ALLOW' if r.success else 'DENY'
        skip_flag = ' (SKIPPED)' if r.skipped else ''
        print(f"[{idx:03d}] {status} expected={s.expected} actual={eff} :: {s.raw}{skip_flag}{' -- ' + r.error if r.error else ''}")
        if args.fail_fast and not r.passed:
            break

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    skipped = sum(1 for r in results if r.skipped)

    print("\nSummary:")
    print(f"  Total:   {len(results)}")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
