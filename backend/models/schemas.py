from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str = Field(description="The natural language query from the business user")
    comparison_target: Optional[str] = Field(None, description="Optional target store/city ID for comparisons")

class PeriodInfo(BaseModel):
    start: str = Field(description="ISO start date (YYYY-MM-DD)")
    end: str = Field(description="ISO end date (YYYY-MM-DD)")
    label: str = Field(description="Human readable period representation e.g. May–July 2026")

class ChartSeries(BaseModel):
    key: str = Field(description="The data key name for this series")
    label: str = Field(description="Human readable display name for this series")
    type: Optional[str] = Field("bar", description="Chart element rendering type e.g. line, bar")

class ChartSpecification(BaseModel):
    type: str = Field(description="Visualization layout type: line, bar, grouped-bar, diagnostic")
    title: str = Field(description="Clear title describing the visual")
    xKey: str = Field(description="The key representing the X-axis category")
    series: List[ChartSeries] = Field(default_factory=list, description="Defined series items for multi-metric displays")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Array of validated data records matching chart specification")

class EvidenceItem(BaseModel):
    label: str = Field(description="The metric name or event context")
    value: str = Field(description="Calculated value representing change or observation")

class VerificationCheck(BaseModel):
    description: str = Field(description="Description of the mathematical recalculation rule")
    result: str = Field(description="Verification outcome: passed or failed")

class VerificationPayload(BaseModel):
    status: str = Field(description="Unified audit outcome: passed or failed")
    checks: List[VerificationCheck] = Field(default_factory=list, description="Detailed checklist of verified calculations")

class QueryResponse(BaseModel):
    question: str = Field(description="Original question asked")
    analysis_type: str = Field(description="Classification of the query intent")
    period: PeriodInfo = Field(description="Dynamically resolved date range boundary details")
    insight: str = Field(description="Primary concise natural language insight summarizing verified facts")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Flexible dictionary containing the relevant analytical metrics")
    chart: ChartSpecification = Field(description="Visual component blueprint mapping calculated data to rendering configurations")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Observed direct variables extracted from database")
    reasoning_basis: List[str] = Field(default_factory=list, description="Array of specific observation items providing explanatory facts")
    verification: VerificationPayload = Field(description="Systematic arithmetic audit result")
    confidence: str = Field(description="Determined operational confidence classification: high, medium, low")
    trace: List[str] = Field(default_factory=list, description="Execution workflow events list")
