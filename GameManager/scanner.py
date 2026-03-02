#!/usr/bin/env python3
"""
Game Manager Scanner
Walks the Side folder, detects project attributes, and compares against catalog.json.
Outputs a report — does NOT auto-update the catalog.

Usage:
  python3 scanner.py              # Compare scan vs catalog
  python3 scanner.py --versions   # Generate versions.json with dependency data
"""

import json
import os
import re
import sys
import glob as globmod
from datetime import datetime, timezone

SIDE_PATH = "/Users/arthurklein/Documents/Work/Side"
CATALOG_PATH = os.path.join(SIDE_PATH, "VibeBash", "GameManager", "catalog.json")
VERSIONS_PATH = os.path.join(SIDE_PATH, "VibeBash", "GameManager", "versions.json")

SKIP_DIRS = {"VibeBash", "Models", "Misc", "ProductFolder", "CollideOScope", "Playland", ".DS_Store"}

TECH_STACK_HINTS = {
    "phaser": "Phaser",
    "@series-inc/venus-sdk": "run.game SDK",
    "@series-inc/rundot-game-sdk": "run.game SDK",
    "three": "Three.js",
    "react": "React",
    "vite": "Vite",
    "@anthropic-ai/sdk": "Anthropic SDK",
    "@supabase/supabase-js": "Supabase",
    "typescript": "TypeScript",
}


def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        return None
    with open(CATALOG_PATH) as f:
        return json.load(f)


def scan_project(project_path, name):
    info = {
        "name": name,
        "path": project_path,
        "hasPackageJson": False,
        "hasGDD": False,
        "hasMilestones": False,
        "hasProductionStatus": False,
        "hasGameConfig": False,
        "hasGit": False,
        "hasReadme": False,
        "hasClaude": False,
        "detectedTech": [],
        "packageName": None,
        "packageVersion": None,
        "milestoneStats": None,
        "dependencies": {},
        "lastModified": None,
    }

    # Check for key files
    info["hasGit"] = os.path.isdir(os.path.join(project_path, ".git"))
    info["hasReadme"] = os.path.exists(os.path.join(project_path, "README.md"))
    info["hasClaude"] = os.path.exists(os.path.join(project_path, "claude.md")) or os.path.exists(os.path.join(project_path, "CLAUDE.md"))
    info["hasGameConfig"] = os.path.exists(os.path.join(project_path, "game.config.json"))
    info["hasProductionStatus"] = os.path.exists(os.path.join(project_path, "PRODUCTION_STATUS.md"))

    # Check for GDD
    gdd_patterns = ["GDD.md", "gdd.md", "*GDD*.md", "*gdd*.md", "*Game Design*.md", "*GDD*.txt", "*gdd*.txt"]
    for pattern in gdd_patterns:
        matches = globmod.glob(os.path.join(project_path, pattern)) + globmod.glob(os.path.join(project_path, "**", pattern), recursive=True)
        if matches:
            info["hasGDD"] = True
            break

    # Check for milestones (root and common subdirectories)
    milestones_path = None
    for subdir in ["", "Design", "docs", "planning"]:
        candidate = os.path.join(project_path, subdir, "MILESTONES.md") if subdir else os.path.join(project_path, "MILESTONES.md")
        if os.path.exists(candidate):
            milestones_path = candidate
            break
    if milestones_path:
        info["hasMilestones"] = True
        info["milestoneStats"] = parse_milestones(milestones_path)

    # Check package.json
    pkg_path = os.path.join(project_path, "package.json")
    if not os.path.exists(pkg_path):
        # Check subdirectories (monorepo pattern)
        for sub in ["game", "frontend", "apps/venus-frontend"]:
            alt = os.path.join(project_path, sub, "package.json")
            if os.path.exists(alt):
                pkg_path = alt
                break

    if os.path.exists(pkg_path):
        info["hasPackageJson"] = True
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
            info["packageName"] = pkg.get("name")
            info["packageVersion"] = pkg.get("version")
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))
            info["dependencies"] = all_deps
            for dep_key, tech_name in TECH_STACK_HINTS.items():
                if dep_key in all_deps:
                    info["detectedTech"].append(tech_name)
        except (json.JSONDecodeError, KeyError):
            pass

    # Walk project to detect tech (if needed) and find latest modification time
    latest_mtime = 0
    extensions = set()
    need_tech = not info["detectedTech"]

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "dist", "build", "__pycache__"}]
        for f in files:
            filepath = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > latest_mtime:
                    latest_mtime = mtime
            except OSError:
                pass
            if need_tech:
                ext = os.path.splitext(f)[1].lower()
                if ext in {".ts", ".tsx"}:
                    extensions.add("TypeScript")
                elif ext in {".js", ".jsx"}:
                    extensions.add("JavaScript")
                elif ext == ".py":
                    extensions.add("Python")

    if need_tech:
        info["detectedTech"] = sorted(extensions)

    if latest_mtime > 0:
        info["lastModified"] = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()

    return info


def parse_milestones(filepath):
    try:
        with open(filepath) as f:
            content = f.read()
    except IOError:
        return None

    total = 0
    completed = 0
    in_progress = 0

    lines = content.split("\n")
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if re.match(r"^###?\s+(MILESTONE|Milestone)\s+\d+", line_stripped):
            total += 1
            # Check status from the header line and the next few lines
            context = line_stripped
            for j in range(1, 4):
                if i + j < len(lines):
                    context += " " + lines[i + j].strip()

            # Look for explicit status markers
            if re.search(r"\*\*Status:\*\*\s*COMPLETE", context, re.IGNORECASE):
                completed += 1
            elif "\u2705" in line_stripped and "NOT STARTED" not in context.upper():
                # ✅ emoji on the header line indicates completed (but check for "% Complete" which means partial)
                if not re.search(r"\d+%\s*Complete", line_stripped, re.IGNORECASE):
                    completed += 1
            elif re.search(r"\*\*Status:\*\*\s*IN.?PROGRESS", context, re.IGNORECASE):
                in_progress += 1
            elif "\U0001f504" in line_stripped:  # 🔄 emoji
                in_progress += 1

    return {"total": total, "completed": completed, "inProgress": in_progress}


def compare_with_catalog(scanned, catalog):
    catalog_slugs = {p["slug"]: p for p in catalog["projects"]} if catalog else {}
    report = []

    for item in scanned:
        name = item["name"]
        slug = name.lower().replace(" ", "").replace("_", "").replace("-", "")

        # Find matching catalog entry
        match = None
        for s, entry in catalog_slugs.items():
            if s == slug or entry["name"].lower().replace(" ", "") == name.lower().replace(" ", ""):
                match = entry
                break

        diffs = []
        if match is None:
            diffs.append("NOT IN CATALOG — consider adding")
        else:
            if item["hasMilestones"] != match.get("hasMilestones", False):
                diffs.append(f"hasMilestones: catalog={match.get('hasMilestones')}, found={item['hasMilestones']}")
            if item["hasGDD"] != match.get("hasGDD", False):
                diffs.append(f"hasGDD: catalog={match.get('hasGDD')}, found={item['hasGDD']}")
            if item["hasProductionStatus"] != match.get("hasProductionStatus", False):
                diffs.append(f"hasProductionStatus: catalog={match.get('hasProductionStatus')}, found={item['hasProductionStatus']}")
            if item["hasGit"] != match.get("gitActive", False):
                diffs.append(f"gitActive: catalog={match.get('gitActive')}, found={item['hasGit']}")
            if item["hasGameConfig"] and not match.get("runGameDeployed", False):
                diffs.append(f"has game.config.json but runGameDeployed=false in catalog")
            if item["milestoneStats"] and match.get("hasMilestones"):
                ms = item["milestoneStats"]
                if ms["total"] != match.get("totalMilestones"):
                    diffs.append(f"totalMilestones: catalog={match.get('totalMilestones')}, found={ms['total']}")
                if ms["completed"] != match.get("completedMilestones"):
                    diffs.append(f"completedMilestones: catalog={match.get('completedMilestones')}, found={ms['completed']}")

        report.append({"name": name, "scanned": item, "catalogMatch": match, "diffs": diffs})

    return report


def print_report(report):
    print("=" * 60)
    print("  GAME MANAGER SCANNER REPORT")
    print("=" * 60)
    print()

    in_sync = 0
    out_of_sync = 0
    missing = 0

    for item in report:
        name = item["name"]
        scanned = item["scanned"]

        indicators = []
        if scanned["hasPackageJson"]: indicators.append("pkg")
        if scanned["hasGit"]: indicators.append("git")
        if scanned["hasMilestones"]: indicators.append("milestones")
        if scanned["hasGDD"]: indicators.append("gdd")
        if scanned["hasGameConfig"]: indicators.append("run.game")
        if scanned["hasProductionStatus"]: indicators.append("prod-status")

        print(f"  {name}")
        print(f"    Found: [{', '.join(indicators) or 'minimal files'}]")
        if scanned["detectedTech"]:
            print(f"    Tech:  {', '.join(scanned['detectedTech'])}")
        if scanned["milestoneStats"]:
            ms = scanned["milestoneStats"]
            print(f"    Milestones: {ms['completed']}/{ms['total']} complete, {ms['inProgress']} in-progress")

        if item["diffs"]:
            if item["catalogMatch"] is None:
                missing += 1
                print(f"    Status: NOT IN CATALOG")
            else:
                out_of_sync += 1
                print(f"    Status: OUT OF SYNC")
            for d in item["diffs"]:
                print(f"      - {d}")
        else:
            in_sync += 1
            print(f"    Status: IN SYNC")

        print()

    print("-" * 60)
    print(f"  Summary: {in_sync} in sync, {out_of_sync} out of sync, {missing} missing from catalog")
    print("-" * 60)


def generate_versions(scanned, catalog):
    """Generate versions.json with dependency data per project, keyed by catalog slug."""
    catalog_slugs = {p["slug"]: p for p in catalog["projects"]} if catalog else {}
    projects = {}

    for item in scanned:
        name = item["name"]
        # Match to catalog slug
        slug = None
        for s, entry in catalog_slugs.items():
            norm_name = name.lower().replace(" ", "").replace("_", "").replace("-", "")
            if s == norm_name or entry["name"].lower().replace(" ", "") == norm_name:
                slug = s
                break

        if slug is None:
            slug = name.lower().replace(" ", "").replace("_", "").replace("-", "")

        if item["dependencies"]:
            projects[slug] = {
                "name": item["name"],
                "dependencies": item["dependencies"],
            }

    versions_data = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projects": projects,
    }

    with open(VERSIONS_PATH, "w") as f:
        json.dump(versions_data, f, indent=2)

    print(f"versions.json generated with {len(projects)} projects at {VERSIONS_PATH}")
    for slug, data in projects.items():
        print(f"  {data['name']}: {len(data['dependencies'])} dependencies")


def scan_all():
    """Scan all projects in the Side folder. Returns list of scan results."""
    scanned = []
    for entry in sorted(os.listdir(SIDE_PATH)):
        if entry in SKIP_DIRS:
            continue
        project_path = os.path.join(SIDE_PATH, entry)
        if not os.path.isdir(project_path):
            continue
        contents = [f for f in os.listdir(project_path) if not f.startswith(".")]
        if not contents:
            continue
        scanned.append(scan_project(project_path, entry))
    return scanned


def main():
    catalog = load_catalog()
    if catalog is None:
        print("Warning: catalog.json not found. Running scan-only mode.")

    scanned = scan_all()

    if "--versions" in sys.argv:
        generate_versions(scanned, catalog)
    else:
        report = compare_with_catalog(scanned, catalog)
        print_report(report)


if __name__ == "__main__":
    main()
