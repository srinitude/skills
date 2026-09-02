export interface ClientRouteSpec {
  command: string;
  id: string;
  mcp: 'not claimed' | 'required';
  route_type: string;
}

export interface ClientRouteResult extends ClientRouteSpec {
  evidence: string;
  status: 'BLOCKED' | 'PASS';
}

export interface ClientSmokeReport {
  archive_sha256: string;
  routes: ClientRouteResult[];
  schema_version: 1;
  skill_count: number;
  skills_sha256: string;
  status: 'BLOCKED' | 'PASS';
}

export interface SmokeContext {
  archiveRoot: string;
  archiveSha256: string;
  cursorReceipt?: string;
  names: string[];
  skillsSha256: string;
  tarball: string;
  temporaryRoot: string;
}
