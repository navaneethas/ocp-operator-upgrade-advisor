export type CompatibilityStatus =
  | 'compatible'
  | 'upgrade_required'
  | 'unsupported'
  | 'manual_intervention';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface AnalysisRequest {
  clusterversion_json: any;
  subscriptions_json: any;
  csv_json: any;
  catalogsource_json: any;
  packagemanifest_json: any;
  target_ocp_version: string;
}

export interface ClusterInfo {
  current_version: string;
  target_version: string;
  total_operators: number;
  compatible_count: number;
  upgrade_required_count: number;
  unsupported_count: number;
  manual_count: number;
}

export interface UpgradePath {
  operator_name: string;
  current_version: string;
  target_version: string;
  path: string[];
  steps: number;
  description: string;
}

export interface CompatibilityResult {
  operator_name: string;
  current_version: string;
  status: CompatibilityStatus;
  target_version?: string;
  supported_versions: string[];
  upgrade_path?: UpgradePath;
  explanation?: string;
  risk_level: RiskLevel;
}

export interface OperatorInfo {
  name: string;
  namespace: string;
  current_csv: string;
  current_version: string;
  channel: string;
  catalog_source: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  timestamp: string;
  cluster_info: ClusterInfo;
  operators: OperatorInfo[];
  compatibility_results: CompatibilityResult[];
  upgrade_paths: Record<string, UpgradePath>;
  ai_summary?: string;
  risk_score: RiskLevel;
}
