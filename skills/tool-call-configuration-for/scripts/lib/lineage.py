"""Rebuild current-byte source lineage after an integration."""
import hashlib

from common import confined, digest_file, load_json, write_json


def collect_ids(value, found):
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            found.add(value["id"])
        for item in value.values():
            collect_ids(item, found)
    elif isinstance(value, list):
        for item in value:
            collect_ids(item, found)


def case_ids(target, names):
    found = set()
    for name in names:
        collect_ids(load_json(confined(target, name)), found)
    return sorted(found)


def public_paths(target, lineage_path):
    return sorted(path.relative_to(target).as_posix() for path in target.rglob("*")
                  if path.is_file() and path != lineage_path
                  and "__pycache__" not in path.parts and path.name != ".DS_Store")


def packet_digest(rows):
    payload = "".join(f"{row['path']}\0{row['sha256']}\n" for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def update_lineage(target, config):
    if not config:
        return
    path = confined(target, config["path"])
    data = load_json(path, "source lineage")
    paths = public_paths(target, path)
    rows = [{"path": name, "sha256": digest_file(confined(target, name))}
            for name in paths]
    data["public_version"] = config["public_version"]
    data["source_case_ids"] = case_ids(target, config.get("case_files", []))
    data["public_files"] = [{"path": name, "source_paths": [name]}
                            for name in paths]
    data["source_files"] = rows
    if config.get("native_manifest") or not data.get("native_manifest_sha256"):
        data["native_manifest_sha256"] = packet_digest(rows)
    write_json(path, data)


def lineage_satisfied(target, config):
    if not config:
        return True
    path = confined(target, config["path"])
    if not path.is_file():
        return False
    data = load_json(path, "source lineage")
    paths = public_paths(target, path)
    hashes = {name: digest_file(confined(target, name)) for name in paths}
    actual_hashes = {row["path"]: row["sha256"]
                     for row in data.get("source_files", [])}
    return (data.get("public_version") == config["public_version"]
            and data.get("source_case_ids") == case_ids(
                target, config.get("case_files", []))
            and actual_hashes == hashes)
