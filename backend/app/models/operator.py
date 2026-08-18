from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CompatibilityStatus(str, Enum):
    COMPATIBLE = "compatible"
    UPGRADE_REQUIRED = "upgrade_required"
    UNSUPPORTED = "unsupported"
    MANUAL_INTERVENTION = "manual_intervention"

class ClusterVersion(BaseModel):
    version: str
    channel: Optional[str] = None
    cluster_id: Optional[str] = None
    upstream: Optional[str] = None

class Subscription(BaseModel):
    name: str
    namespace: str
    package: str
    channel: str
    source: str
    source_namespace: str
    current_csv: Optional[str] = None
    installed_csv: Optional[str] = None

class CSV(BaseModel):
    name: str
    namespace: str
    version: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    replaces: Optional[str] = None
    skips: Optional[List[str]] = []
    skip_range: Optional[str] = None

class CatalogSource(BaseModel):
    name: str
    namespace: str
    display_name: Optional[str] = None
    publisher: Optional[str] = None
    source_type: str
    image: Optional[str] = None

class PackageChannel(BaseModel):
    name: str
    current_csv: str
    current_csv_version: Optional[str] = None

class PackageManifest(BaseModel):
    package_name: str
    catalog_source: str
    catalog_source_namespace: str
    default_channel: Optional[str] = None
    channels: List[PackageChannel] = []

class OperatorInfo(BaseModel):
    name: str
    namespace: str
    current_csv: str
    current_version: str
    channel: str
    catalog_source: str
    subscription: Optional[Subscription] = None
    package_manifest: Optional[PackageManifest] = None

class UpgradePath(BaseModel):
    operator_name: str
    current_version: str
    target_version: str
    path: List[str]
    steps: int
    description: Optional[str] = None

class CompatibilityResult(BaseModel):
    operator_name: str
    current_version: str
    status: CompatibilityStatus
    target_version: Optional[str] = None
    supported_versions: List[str] = []
    upgrade_path: Optional[UpgradePath] = None
    explanation: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW

class AnalysisRequest(BaseModel):
    clusterversion_json: Dict[str, Any]
    subscriptions_json: Dict[str, Any]
    csv_json: Dict[str, Any]
    catalogsource_json: Dict[str, Any]
    packagemanifest_json: Dict[str, Any]
    target_ocp_version: str

class ClusterInfo(BaseModel):
    current_version: str
    target_version: str
    total_operators: int
    compatible_count: int
    upgrade_required_count: int
    unsupported_count: int
    manual_count: int

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: datetime
    cluster_info: ClusterInfo
    operators: List[OperatorInfo]
    compatibility_results: List[CompatibilityResult]
    upgrade_paths: Dict[str, UpgradePath]
    ai_summary: Optional[str] = None
    risk_score: RiskLevel

class ChatRequest(BaseModel):
    analysis_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    context_used: bool
